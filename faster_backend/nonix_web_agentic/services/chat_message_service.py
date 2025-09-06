import asyncio
import importlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, AsyncGenerator, TYPE_CHECKING

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from nonix_web.utils.di import Inject
from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..llm.agentic_tool_manager import AgenticToolManager
from nonix_web.web_socket_service import WebSocketService
from ..llm.llm_message_utils import LCAIMessage, LCToolMessage, iter_messages
from ..models.ai_model_mapping import AIModelMapping
from ..models.ai_provider import AIProvider
from ..models.chat_history import ChatHistory
from ..models.chat_message import ChatMessage
from ..models.chat_session import ChatSession
from ..models.persona import Persona
from ..models.tool_invocation_log import ToolInvocationLog
from ..schemas.chat_message_schemas import ChatMessageCreate, ChatMessageUpdate, ChatMessageInDbModel, SendMessageToHistoryRequest
from ..sequence_utils import next_seq
from ..services.chat.message_handlers import ChatMessageHandler, ToolCallMessageHandler
from ..services.chat.message_type_registry import message_type_registry
from ..services.chat.streaming_event_manager import StreamingEventManager
from ..services.chat.streaming_interface import StreamingChunk
from ..services.chat.streaming_message_handler import StreamingMessageHandler
from ..services.chat.task_manager import ChatTaskManager

if TYPE_CHECKING:
    from ..plugin import NxWebAgenticPlugin
    from nonix_template.plugin import NxWebTemplatePlugin


class ChatMessageService(BaseCrudService):
    config = CRUDConfig(
        model=ChatMessage,
        create_schema=ChatMessageCreate,
        update_schema=ChatMessageUpdate,
        response_schema=ChatMessageInDbModel,
        filters=FilterConfig(
            allowed_fields=['history_id', 'role', 'message_type']
        ),
        sorting=SortingConfig(
            default_sort='seq',
            allowed_fields=['seq', 'created_at', 'id', 'role']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['role', 'message_type'],
            display_format='{role}',
            search_fields=['role'],
            order_by='created_at'
        )
    )

    agentic_plugin: "NxWebAgenticPlugin" = Inject("agentic")
    template_plugin: "NxWebTemplatePlugin" = Inject("template")
    agentic_tool_manager: AgenticToolManager = Inject(AgenticToolManager)
    web_socket_service: WebSocketService = Inject(WebSocketService)

    def __init__(self):
        """Initialize message type handlers."""
        # Register message type handlers (meta-types)
        super().__init__()
        message_type_registry.register('user', ChatMessageHandler())
        message_type_registry.register('tool_call', ToolCallMessageHandler())
        self._task_manager = ChatTaskManager()

    async def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        room = f'chat/{session_id}/{history_id}'
        await self.web_socket_service.send_ws_message(room, {
            'event': event,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def emit_llm_event(self, session_id: int, history_id: int, stage: str, message: str) -> None:
        await self.emit_chat_event(session_id, history_id, 'llm_status', {
            'stage': stage,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def render_persona_prompt(self, persona, artist=None, context=None):
        """Render LLM system prompt for persona using template plugin"""
        # Prepare context variables - let template handle all conditional logic
        template_vars = {
            'persona': persona,
            'artist': artist,
        }

        # Add any additional context
        if context:
            template_vars.update(context)

        # Render template using the new template plugin
        # Template handles all conditional logic (artist checks, etc.)
        return await self.template_plugin.render_template(
            "llm_instructions/persona_system_prompt",
            context=template_vars
        )

    async def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra) -> None:
        await self.emit_chat_event(session_id, history_id, 'tool_status', {
            'tool_name': tool_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            **extra
        })

    async def submit_async_task(self, func, *args, **kwargs):
        try:
            future = await self._task_manager.submit_task(func, *args, **kwargs)
            self._logger.debug(f"Task submitted to task manager: {func.__name__}")
            return future
        except Exception as e:
            self._logger.error(f"Failed to submit task to task manager: {e}", exc_info=True)
            raise

    async def _select_chat_model(self, persona_id: int) -> Dict[str, Any] | None:
        """Select AI model for persona with strict validation."""
        self._logger.debug(f"Selecting AI model for persona {persona_id}")

        async with AsyncSessionLocal() as db_session:
            persona = (await db_session.execute(
                select(Persona).where(Persona.id == persona_id)
            )).scalar_one_or_none()

            if not persona:
                self._logger.warning(f"Persona {persona_id} not found")
                return None

            mapping = None
            if persona and getattr(persona, 'ai_model_mapping_id', None):
                mapping = (await db_session.execute(
                    select(AIModelMapping).where(AIModelMapping.id == persona.ai_model_mapping_id,
                                                 AIModelMapping.is_active == True)
                )).scalar_one_or_none()
                self._logger.debug(f"AI model mapping found: {mapping}")
            else:
                self._logger.warning(f"Persona {persona_id} has no AI model mapping")

            if not mapping:
                self._logger.warning(f"No active AI model mapping found for persona {persona_id}")
                return None

            model_info = {
                'provider_id': mapping.provider_id,
                'model_name': mapping.model_name,
                'parameters': mapping.parameters_json or {},
            }
            self._logger.info(f"Selected AI model: {mapping.model_name} (provider: {mapping.provider_id})")
            return model_info

    async def _validate_session_history(self, session_id: int, history_id: int = None):
        """Validate session and history, return tuple (session, history)."""
        self._logger.debug(f"Validating session {session_id} with history {history_id}")

        async with AsyncSessionLocal() as db_session:
            # Load session with persona relationship eagerly
            session_result = await db_session.execute(
                select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
            )
            session = session_result.scalar_one_or_none()

            if not session:
                self._logger.warning(f"Session {session_id} not found or inactive")
                return None, None

            # Load persona relationship eagerly to avoid detached instance errors
            await db_session.refresh(session, ['persona'])

            if history_id:
                # Specific history requested
                self._logger.debug(f"Querying history {history_id} for session {session_id}")

                history_result = await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )
                history = history_result.scalar_one_or_none()
                self._logger.debug(f"History query result: {history}")

                if not history:
                    self._logger.warning(f"History {history_id} not found for session {session_id}")
                    return session, None
            else:
                # Use current history or create new one
                if not session.current_history_id:
                    self._logger.info(f"Creating new history for session {session_id}")
                    history = ChatHistory(
                        session_id=session_id,
                        title='New Conversation',
                        message_count=0
                    )
                    db_session.add(history)
                    await db_session.commit()
                    await db_session.refresh(history)
                    session.current_history_id = history.id
                    await db_session.commit()
                    self._logger.info(f"New history {history.id} created for session {session_id}")
                else:
                    self._logger.debug(f"Using existing history {session.current_history_id} for session {session_id}")
                    history = await db_session.get(ChatHistory, session.current_history_id)
                    if not history:
                        self._logger.warning(
                            f"Current history {session.current_history_id} not found for session {session_id}")
                        return session, None

            self._logger.debug(
                f"Session validation successful: session={session.id}, history={history.id if history else None}")
            return session, history

    async def _create_user_message(self, history_id: int, content: Dict[str, Any]) -> ChatMessage:
        self._logger.debug(f"Creating user message for history {history_id}")

        async with AsyncSessionLocal() as db_session:
            user_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='user',
                content_json=content,
                status='complete'
            )
            db_session.add(user_msg)
            await db_session.commit()
            await db_session.refresh(user_msg)

            self._logger.info(f"User message {user_msg.id} created successfully for history {history_id}")
            return user_msg

    async def create_assistant_placeholder(self, history_id: int) -> ChatMessage:
        """Create empty assistant message placeholder."""
        self._logger.debug(f"Creating assistant message placeholder for history {history_id}")

        async with AsyncSessionLocal() as db_session:
            seq_val = await next_seq(history_id)
            turn = str(uuid.uuid4())
            asst_msg = ChatMessage(
                history_id=history_id,
                role='assistant',
                message_type='assistant',
                content_json={'text': ''},
                status='processing',
                seq=seq_val,
                turn_id=turn
            )
            db_session.add(asst_msg)
            await db_session.commit()
            await db_session.refresh(asst_msg)

            self._logger.info(f"Assistant message placeholder {asst_msg.id} created for history {history_id}")
            return asst_msg

    async def _build_chat_history(self, history_id: int, user_msg_id: int) -> List[Dict[str, Any]]:
        """Build chat history for LLM processing."""
        self._logger.debug(f"Building chat history for history {history_id} up to message {user_msg_id}")

        async with AsyncSessionLocal() as db_session:
            chat_history = []

            # Add user and assistant messages up to current user message
            user_result = await db_session.execute(
                select(ChatMessage).where(ChatMessage.history_id == history_id,
                                          ChatMessage.id <= user_msg_id).order_by(
                    ChatMessage.seq.asc())
            )
            user_msgs = user_result.scalars().all()
            self._logger.debug(f"Found {len(user_msgs)} user/assistant messages")
            for um in user_msgs:
                role = um.role
                if role not in ('user', 'assistant'):
                    continue
                content = um.content_json if isinstance(um.content_json, dict) else {'text': str(um.content_json)}
                chat_history.append({'role': role, 'content': content})

            self._logger.info(f"Built chat history with {len(chat_history)} total messages")
            return chat_history

    async def _resolve_ai_model(self, persona_id: int):
        """Resolve AI model, provider, and mapping."""
        self._logger.debug(f"Resolving AI model components for persona {persona_id}")

        model_info = await self._select_chat_model(persona_id)
        if not model_info:
            self._logger.warning(f"Failed to select AI model for persona {persona_id}")
            return None, None, None

        async with AsyncSessionLocal() as db_session:
            provider = (await db_session.execute(
                select(AIProvider).where(AIProvider.id == model_info['provider_id'], AIProvider.is_active == True)
            )).scalar_one_or_none()

            if not provider:
                self._logger.warning(f"AI provider {model_info['provider_id']} not found or inactive")
                return None, None, None

            # FIX: use persona.ai_model_mapping_id rather than persona_id
            mapping_obj = (await db_session.execute(
                select(AIModelMapping).where(AIModelMapping.id == (await db_session.execute(
                    select(Persona.ai_model_mapping_id).where(Persona.id == persona_id)
                )).scalar_one_or_none(), AIModelMapping.is_active == True)
            )).scalar_one_or_none()

            if not mapping_obj:
                self._logger.warning(f"AI model mapping not found or inactive for persona {persona_id}")
                return None, None, None

            self._logger.info(
                f"AI model resolved successfully: provider={provider.name}, model={model_info['model_name']}")
            return model_info, provider, mapping_obj

    async def list_messages(self, session_id: int):
        """List messages from a chat session's current history."""
        try:
            async with AsyncSessionLocal() as db_session:
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    raise ValueError('Session not found or inactive')

                # Get messages from current history
                if not session.current_history_id:
                    return []

                msgs = (await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == session.current_history_id).order_by(
                        ChatMessage.seq.asc())
                )).scalars().all()

                return [m.to_dict() for m in msgs]
        except Exception as exc:
            raise exc

    async def list_history_messages(self, session_id: int, history_id: int):
        """List messages from a specific history within a session."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Validate session exists
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    raise ValueError('Session not found or inactive')

                # Validate history belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    raise ValueError('History not found or does not belong to session')

                # Get messages from specific history
                msgs = (await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == history_id).order_by(
                        ChatMessage.seq.asc())
                )).scalars().all()

                return [m.to_dict() for m in msgs]
        except Exception as exc:
            raise exc

    async def send_message(self, session_id: int, history_id: int, payload: SendMessageToHistoryRequest):
        """Send message to session."""
        self._logger.info(f"Processing send_message request for session {session_id}, history {history_id}")

        try:
            session_id = int(session_id)
            if history_id:
                history_id = int(history_id)

            self._logger.debug(f"Parameter conversion: session_id={session_id}, history_id={history_id}")

            session, history = await self._validate_session_history(session_id, history_id)
            if not session:
                self._logger.warning(f"Session {session_id} not found")
                raise ValueError('Session not found')

            persona = session.persona
            if not persona:
                self._logger.warning(f"Session {session_id} has no persona")
                raise ValueError('Session has no persona')
            if not persona.is_active:
                self._logger.warning(f"Persona {persona.id} is not active")
                raise ValueError('Persona is not active')

            if not history_id:
                self._logger.debug(
                    f"No history_id provided, using session.current_history_id: {session.current_history_id}")
                history_id = session.current_history_id
                if not history_id:
                    self._logger.warning(f"No current history found for session {session_id}")
                    raise ValueError('No current history')

            # Validate provided history_id belongs to session
            if not history or history.session_id != session_id:
                self._logger.warning(f"History validation failed - history: {history}, session_id: {session_id}")
                raise ValueError('History not found or invalid')

            # Get user content (object)
            user_content = payload.content
            if not user_content:
                raise ValueError('content required')

            # Enforce explicit meta-type from frontend (top-level message_type only)
            message_type = getattr(payload, 'message_type', None)
            if not message_type:
                raise ValueError('message_type is required')

            self._logger.info(f"Processing message type: {message_type}")
            self._logger.debug(f"Available message types: {message_type_registry.list_types()}")
            self._logger.debug(
                f"Handler found for type '{message_type}': {message_type_registry.has_handler(message_type)}")

            # Get handler from registry
            handler = message_type_registry.get_handler(message_type)
            self._logger.debug(f"Message handler resolved: {type(handler).__name__}")
            if not handler:
                self._logger.error(f"Unknown message type: {message_type}")
                raise ValueError(f'Unknown message type: {message_type}')

            result = await handler.handle(
                chat_service=self,
                session=session,
                persona=persona,
                history_id=history_id,  # ALWAYS provided (extracted or from URL)
                content=user_content
            )

            self._logger.info(f"Message processed successfully by handler, returning result")
            return result

        except Exception as exc:
            self._logger.error(f"Error in send_message: {exc}", exc_info=True)
            raise exc

    async def run_chat_streaming(self, provider: Any, mapping: Any, messages: List[Dict[str, Any]],
                                 available_tools_info: List[Dict[str, Any]], persona_id: int) -> AsyncGenerator[
        StreamingChunk, None]:
        """Run chat streaming with LLM integration."""
        cfg: Dict[str, Any] = provider.config_json or {}
        model_name: str = mapping.model_name
        params: Dict[str, Any] = mapping.parameters_json or {}

        module_name: str = getattr(provider, 'module', '') or ''
        class_name: str = getattr(provider, 'cls', '') or ''

        if not module_name or not class_name:
            # Fallback: echo last user
            last_user = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
            text = (last_user or {}).get('content', '')
            if isinstance(text, dict):
                text = text.get('text', str(text))
            yield StreamingChunk(
                content=f"Provider not configured (module/class missing). Echo: {text}",
                chunk_type="complete",
                is_final=True
            )
            return

        # Build kwargs: provider creds/connection + model + mapping params (mapping overrides)
        kwargs: Dict[str, Any] = {}
        kwargs.update(cfg or {})
        kwargs['model'] = model_name
        kwargs.update(params or {})

        try:
            module = importlib.import_module(module_name)
            client_cls = getattr(module, class_name)
        except Exception as exc:  # noqa: BLE001
            self._logger.error(f"Provider import error: {exc}", exc_info=True)
            error_message = self._format_user_friendly_error(exc, "provider_config_error")
            yield StreamingChunk(content=error_message, chunk_type="error", is_final=True)
            return

        try:
            client = client_cls(**kwargs)

            # Create LangChain tools (can be empty list if no tools)
            langchain_tools = []
            if available_tools_info is not None:
                langchain_tools = await self.agentic_tool_manager.create_langchain_tools(
                    persona_id,
                    available_tools_info
                )
                self._logger.info(f"🔧 Created {len(langchain_tools)} LangChain tools for persona {persona_id}")

            persona_system_prompt = ""
            async with AsyncSessionLocal() as db_session:
                persona_result = await db_session.execute(
                    select(Persona).options(selectinload(Persona.artist))
                    .where(Persona.id == persona_id)
                )
                persona = persona_result.scalar_one_or_none()
                if persona:
                    persona_system_prompt = await self.render_persona_prompt(
                        persona=persona,
                        artist=persona.artist if persona.artist else None,
                        context={'persona_id': persona_id, 'timestamp': datetime.now()}
                    )

            template_messages = [
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
            # Create the ChatPromptTemplate with persona system prompt
            if persona_system_prompt:
                template_messages.insert(0, ("system", persona_system_prompt), )
            chat_prompt = ChatPromptTemplate.from_messages(template_messages)

            agent = create_react_agent(client, tools=langchain_tools)

            self._logger.info(f"🔧 Created ReAct agent with {len(langchain_tools)} tools")

            # Chain the prompt with the agent
            new_agent = chat_prompt | agent

            # Get the last user message
            last_user_msg = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
            if last_user_msg:
                user_content = last_user_msg.get('content', '')
                if isinstance(user_content, dict):
                    user_content = user_content.get('text', str(user_content))

                # Build conversation history as tuples aligned with ChatPromptTemplate
                conversation_history = []
                for m in messages:
                    role = m.get('role')
                    content = m.get('content')
                    if isinstance(content, dict):
                        content = content.get('text', str(content))
                    if role == 'user':
                        conversation_history.append(("human", content))
                    elif role == 'assistant':
                        conversation_history.append(("ai", content))
                    elif role == 'system':
                        pass

                # Use streaming with astream_events
                async for mode, message in iter_messages(new_agent.astream_events({
                    "chat_history": conversation_history,
                    "input": user_content
                })):
                    if mode == "start":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content="", chunk_type="ai_start", metadata={
                                "run_id": message.msg_id,
                                "parent_ids": message.status.get("parent_ids", [])
                            })
                            initial_content = message.status.get("content", "")
                            if initial_content:
                                yield StreamingChunk(content=initial_content, chunk_type="text", metadata={
                                    "run_id": message.msg_id,
                                    "parent_ids": message.status.get("parent_ids", [])
                                })
                        elif isinstance(message, LCToolMessage):
                            yield StreamingChunk(
                                content="",
                                chunk_type="tool_start",
                                metadata={
                                    "tool_name": message.status.get("tool_name", "unknown"),
                                    "args": message.status.get("input", {}),
                                    "run_id": message.msg_id,
                                    "tool_run_id": message.msg_id,
                                    "parent_ids": message.status.get("parent_ids", [])
                                }
                            )

                    elif mode == "update":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content=message.status.get("content", ""), chunk_type="text",
                                                 metadata={
                                                     "run_id": message.msg_id,
                                                     "parent_ids": message.status.get("parent_ids", [])
                                                 })

                    elif mode == "end":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content="", chunk_type="complete", is_final=True, metadata={
                                "run_id": message.msg_id,
                                "parent_ids": message.status.get("parent_ids", [])
                            })
                        elif isinstance(message, LCToolMessage):
                            raw_output = message.get_status("output")
                            parsed = None
                            # Normalize LangChain ToolMessage output to JSON-serializable exec_result
                            if hasattr(raw_output, 'content'):
                                content_text = raw_output.content
                                try:
                                    parsed = json.loads(content_text)
                                except Exception:
                                    parsed = {"success": False, "error": "Non-JSON tool output",
                                              "content": content_text}
                            else:
                                parsed = raw_output if isinstance(raw_output, (dict, list, str, int, float, bool,
                                                                               type(None))) else {
                                    "value": str(raw_output)}

                            status_val = 'success' if isinstance(parsed, dict) and parsed.get(
                                'success') is True else 'error'
                            exec_result = {"status": status_val, "result": parsed}

                            yield StreamingChunk(
                                content="",
                                chunk_type="tool_end",
                                metadata={
                                    "tool_name": message.status.get("tool_name", "unknown"),
                                    "result": exec_result,
                                    "run_id": message.msg_id,
                                    "tool_run_id": message.msg_id,
                                    "parent_ids": message.status.get("parent_ids", [])
                                }
                            )

            else:
                error_message = "No user message found. Please try sending a message again."
                yield StreamingChunk(content=error_message, chunk_type="error", is_final=True)

        except Exception as exc:  # noqa: BLE001
            self._logger.error(f"Provider error: {exc}", exc_info=True)
            error_message = self._format_user_friendly_error(exc, "connection_error")
            yield StreamingChunk(content=error_message, chunk_type="error", is_final=True)

    async def run_chat_streaming_with_retry(self, provider, mapping, messages, available_tools_info, persona_id,
                                            max_retries: int = 2):
        """Run chat streaming with automatic retry for connection errors."""
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                async for chunk in self.run_chat_streaming(provider, mapping, messages, available_tools_info,
                                                           persona_id):
                    yield chunk
                return  # Success, exit retry loop

            except Exception as exc:
                last_exception = exc

                # Check if this is a retryable error
                if not self._is_retryable_error(exc):
                    break

                # Don't retry on last attempt
                if attempt >= max_retries:
                    break

                # Calculate delay with exponential backoff
                delay = min(1.0 * (2 ** attempt), 10.0)

                # Log retry attempt
                self._logger.warning(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s for error: {exc}")

                # Wait before retry
                await asyncio.sleep(delay)

        # All retries exhausted, yield error chunk
        error_message = f"Service unavailable after {max_retries} attempts. Please try again later."
        yield StreamingChunk(content=error_message, chunk_type="error", is_final=True)

    def _is_retryable_error(self, exc: Exception) -> bool:
        """Determine if an error is retryable."""
        retryable_errors = [
            "Connection error",
            "All connection attempts failed",
            "APIConnectionError",
            "ConnectError",
            "TimeoutError"
        ]

        error_str = str(exc)
        return any(retryable in error_str for retryable in retryable_errors)

    def _format_user_friendly_error(self, exc: Exception, error_type: str) -> str:
        """Format error messages for end users."""
        error_messages = {
            "connection_error": "Unable to connect to AI service. Please check your internet connection and try again.",
            "provider_config_error": "AI service configuration error. Please contact support.",
            "api_connection_error": "AI service is currently unavailable. Please try again later.",
            "general_error": "An error occurred while processing your request. Please try again."
        }
        return error_messages.get(error_type, "An unexpected error occurred. Please try again.")

    async def submit_message_for_async_processing(self, user_msg_id: int, asst_msg_id: int, session_id: int,
                                                  history_id: int, persona_id: int):
        """Submit message processing to task manager for async execution."""
        try:
            # Use the task manager from the parent ChatRouter with session tracking
            future = await self.submit_async_task(
                self._process_message_async,
                session_id,
                user_msg_id,
                asst_msg_id,
                history_id,
                persona_id,
                session_id
            )

            # Tag task with assistant message id for per-request cancellation
            try:
                setattr(future, '_assistant_message_id', asst_msg_id)
            except Exception:
                pass

            # Log successful submission with proper logger
            self._logger.info(
                f"Message {user_msg_id} submitted to task manager for async processing (session: {session_id})")
            return future

        except Exception as e:
            # Log error with full stack trace
            self._logger.error(f"Failed to submit message {user_msg_id} to task manager: {e}", exc_info=True)
            # Emit error event
            await self.emit_llm_event(session_id, history_id, 'processing_failed', f'Failed to start processing: {e}')
            raise

    async def clear_history_messages(self, session_id: int, history_id: int):
        """Clear all messages from a specific history with validation."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Verify session exists and is active
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    raise ValueError('Session not found or inactive')

                # Verify history exists and belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    raise ValueError('History not found')

                # Count messages before deletion
                messages_result = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == history_id)
                )
                messages = messages_result.scalars().all()
                deleted_count = len(messages)

                # Delete tool invocation logs
                logs_result = await db_session.execute(
                    select(ToolInvocationLog).where(ToolInvocationLog.history_id == history_id)
                )
                logs = logs_result.scalars().all()
                for log in logs:
                    await db_session.delete(log)

                # Delete all messages in the history
                for message in messages:
                    await db_session.delete(message)

                # Reset history message count
                history.message_count = 0

                await db_session.commit()

                return {
                    'message': f'Successfully cleared {deleted_count} messages from history',
                    'deleted_count': deleted_count
                }

        except Exception as exc:
            raise exc

    async def delete_message_with_validation(self, session_id: int, history_id: int, message_id: int):
        """Delete a specific message with session/history validation."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Verify session exists and is active
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    raise ValueError('Session not found or inactive')

                # Verify history exists and belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    raise ValueError('History not found')

                # Find and delete the specific message
                message = (await db_session.execute(
                    select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.history_id == history_id)
                )).scalar_one_or_none()

                if not message:
                    raise ValueError('Message not found')

                # Store message ID before deletion for response
                deleted_message_id = message.id

                # Delete associated tool invocation logs
                logs_result = await db_session.execute(
                    select(ToolInvocationLog).where(ToolInvocationLog.message_id == message.id)
                )
                logs = logs_result.scalars().all()
                for log in logs:
                    await db_session.delete(log)

                # Delete the message
                await db_session.delete(message)

                # Update history message count
                history.message_count = max(0, history.message_count - 1)

                await db_session.commit()

                return {
                    'message': 'Message deleted successfully',
                    'deleted_message_id': deleted_message_id
                }

        except Exception as exc:
            raise exc

    async def cancel_message_streaming(self, session_id: int, history_id: int, assistant_message_id: int):
        """Cancel streaming for a single assistant message."""
        try:
            # Validate session and history exist and match
            session, history = await self._validate_session_history(session_id, history_id)
            if not session or not history:
                raise ValueError('Session or history not found')

            # Find and cancel the task tagged with this assistant_message_id
            cancelled = False
            try:
                active = getattr(self._task_manager, '_active_tasks', [])
                for task in list(active):
                    try:
                        if getattr(task, '_assistant_message_id', None) == assistant_message_id and not task.done():
                            task.cancel()
                            cancelled = True
                            break
                    except Exception:
                        continue
            except Exception:
                cancelled = False

            return {
                'message': 'Cancelled message task' if cancelled else 'No active task for message',
                'assistant_message_id': assistant_message_id,
                'cancelled': cancelled
            }
        except Exception as exc:
            raise exc

    async def retry_last_message(self, session_id: int):
        """Retry the last user message in a session."""
        try:
            # Validate session exists
            session, history = await self._validate_session_history(session_id)
            if not session:
                raise ValueError('Session not found or inactive')

            # Get the last user message
            last_user_msg = await self._get_last_user_message(session_id)
            if not last_user_msg:
                raise ValueError('No user messages to retry')

            # Create new assistant message placeholder
            asst_msg = await self.create_assistant_placeholder(history.id if history else session.current_history_id)

            # Submit for retry processing
            future = await self.submit_message_for_async_processing(
                last_user_msg.id,
                asst_msg.id,
                session_id,
                history.id if history else session.current_history_id,
                session.persona_id
            )

            return {
                'message': 'Message retry initiated',
                'session_id': session_id,
                'user_message_id': last_user_msg.id,
                'assistant_message_id': asst_msg.id,
                'status': 'processing'
            }
        except Exception as exc:
            raise exc

    async def get_last_user_message(self, session_id: int):
        """Get the last user message content for retry functionality."""
        try:
            # Validate session exists
            session, _ = await self._validate_session_history(session_id)
            if not session:
                raise ValueError('Session not found or inactive')

            # Get the last user message content
            last_message_content = await self._get_last_user_message_content(session_id)
            if not last_message_content:
                raise ValueError('No user messages found')

            return {
                'session_id': session_id,
                'last_message': last_message_content,
                'can_retry': True
            }
        except Exception as exc:
            raise exc

    async def _process_message_async(
            self,
            user_msg_id: int,
            asst_msg_id: int,
            history_id: int,
            persona_id: int,
            session_id: int
    ):
        """Process message asynchronously using streaming."""
        message_handler = StreamingMessageHandler(session_id, history_id)
        event_manager = StreamingEventManager(self)
        accumulated_text = ""
        try:
            # Set the existing assistant message ID
            message_handler.assistant_message_id = asst_msg_id
            # Load assistant message to propagate seq/turn_id
            async with AsyncSessionLocal() as meta_session:
                asst_msg_obj = await meta_session.get(ChatMessage, asst_msg_id)
                asst_seq = getattr(asst_msg_obj, 'seq', None)
                asst_turn = getattr(asst_msg_obj, 'turn_id', None)

            # Validate message exists
            if not await message_handler.ensure_message_exists():
                error_msg = "Assistant message not found or inaccessible"
                await self.emit_llm_event(session_id, history_id, 'processing_failed', error_msg)
                return

            # Get model info and tools
            model_info, provider, mapping_obj = await self._resolve_ai_model(persona_id)
            available_tools_info = await self.agentic_tool_manager.list_persona_tools(persona_id)
            if not model_info or not provider or not mapping_obj:
                # No model available - mark as failed
                error_msg = "AI model, provider, or mapping not available"
                await message_handler.mark_as_error(error_msg)
                await event_manager.emit_chunk_event(
                    session_id,
                    history_id,
                    StreamingChunk(content="", chunk_type="complete", is_final=True),
                    asst_msg_id
                )
                return

            # Build chat history using helper method
            chat_history = await self._build_chat_history(history_id, user_msg_id)

            # Use streaming LLM client with retry
            try:
                async for message in self.run_chat_streaming_with_retry(
                        provider,
                        mapping_obj,
                        chat_history,
                        available_tools_info,
                        persona_id,
                        max_retries=2
                ):
                    # message is already a StreamingChunk

                    # Handle each chunk
                    if message.chunk_type == "text":
                        # accumulate full text for final persistence
                        accumulated_text += message.content or ""
                        message.metadata = message.metadata or {}
                        if asst_seq is not None:
                            message.metadata['seq'] = asst_seq
                        if asst_turn is not None:
                            message.metadata['turn_id'] = asst_turn
                        if await message_handler.update_content_safely(message.content):
                            await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)
                        else:
                            # Log error but continue processing
                            self._logger.error(f"Failed to update content for chunk: {message.content[:50]}...")

                    elif message.chunk_type == "ai_start":
                        message.metadata = message.metadata or {}
                        if asst_seq is not None:
                            message.metadata['seq'] = asst_seq
                        if asst_turn is not None:
                            message.metadata['turn_id'] = asst_turn
                        await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)

                    elif message.chunk_type == "tool_start":
                        tool_name = message.metadata.get("tool_name", "")
                        tool_args = message.metadata.get("args", {})
                        tool_run = message.metadata.get("tool_run_id")
                        run_id = message.metadata.get("run_id")
                        parent_ids = message.metadata.get("parent_ids", [])

                        # ✅ FIXED: Create tool_call message for LangChain tool execution
                        async with AsyncSessionLocal() as db_session:
                            # Create ToolInvocationLog for LangChain tool execution
                            log = ToolInvocationLog(
                                history_id=history_id,
                                message_id=user_msg_id,  # Use the current user message ID
                                tool_name=tool_name,
                                input_json=tool_args,
                                status='started',
                                seq=await next_seq(history_id),
                                turn_id=asst_turn,
                                run_id=run_id,
                                parent_ids=parent_ids,
                                tool_run_id=tool_run
                            )
                            db_session.add(log)
                            await db_session.commit()
                            await db_session.refresh(log)

                            tool_call_msg = ChatMessage(
                                history_id=history_id,
                                role='user',
                                message_type='tool_call',
                                content_json={
                                    'tool_name': tool_name,
                                    'tool_args': tool_args,
                                    'executed_by': 'llm',
                                    'execution_time': datetime.now(timezone.utc).isoformat(),
                                    'execution_path': 'langchain'
                                },
                                status='complete',
                                seq=await next_seq(history_id),
                                turn_id=asst_turn,
                                tool_run_id=tool_run,
                                run_id=run_id,
                                parent_ids=parent_ids
                            )
                            db_session.add(tool_call_msg)
                            await db_session.commit()
                            await db_session.refresh(tool_call_msg)

                            # Emit WebSocket event for tool call message (top-level fields only)
                            await self.emit_chat_event(session_id, history_id, 'message_received', {
                                'message_id': tool_call_msg.id,
                                'role': tool_call_msg.role,
                                'message_type': 'tool_call',
                                'status': 'complete',
                                'tool_name': tool_name,
                                'tool_args': tool_args,
                                'executed_by': 'llm',
                                'execution_time': tool_call_msg.content_json.get('execution_time'),
                                'execution_path': 'langchain',
                                'seq': tool_call_msg.seq,
                                'turn_id': tool_call_msg.turn_id,
                                'tool_run_id': tool_call_msg.tool_run_id,
                                'run_id': tool_call_msg.run_id,
                                'parent_ids': parent_ids,
                                'timestamp': tool_call_msg.created_at.isoformat()
                            })

                        await event_manager.emit_tool_event(
                            session_id,
                            history_id,
                            tool_name,
                            "started",
                            args=tool_args,
                            seq=tool_call_msg.seq,
                            turn_id=tool_call_msg.turn_id,
                            tool_run_id=tool_run,
                            run_id=run_id,
                            parent_ids=parent_ids
                        )

                    elif message.chunk_type == "tool_end":
                        tool_name = message.metadata.get("tool_name", "")
                        tool_args = message.metadata.get("args", {})
                        tool_run = message.metadata.get("tool_run_id")
                        run_id = message.metadata.get("run_id")
                        parent_ids = message.metadata.get("parent_ids", [])

                        # ✅ FIXED: Create tool_result message for LangChain tool execution
                        # Note: LangChain may not provide detailed result in metadata, so we create a basic message
                        async with AsyncSessionLocal() as db_session:
                            # Update ToolInvocationLog with completion status
                            # Find the log entry created during tool_start
                            log_result = await db_session.execute(
                                select(ToolInvocationLog).where(
                                    ToolInvocationLog.history_id == history_id,
                                    ToolInvocationLog.tool_run_id == tool_run,
                                    ToolInvocationLog.status == 'started'
                                ).order_by(ToolInvocationLog.created_at.desc())
                            )
                            existing_log = log_result.scalar_one_or_none()
                            if existing_log:
                                existing_log.status = 'success'  # Assume success for LangChain tools
                                existing_log.output_json = message.metadata.get("result", {"status": "completed"})
                                await db_session.commit()

                            tool_result_msg = ChatMessage(
                                history_id=history_id,
                                role='tool',
                                message_type='tool_result',
                                status='complete',  # ✅ FIXED: Add required status field
                                content_json={
                                    'tool_name': tool_name,
                                    'tool_args': tool_args,
                                    'execution_status': 'completed',  # LangChain handled the execution
                                    'result': message.metadata.get("result", {"status": "completed"}),
                                    'executed_by': 'llm',
                                    'execution_time': datetime.now(timezone.utc).isoformat(),
                                    'execution_path': 'langchain'
                                },
                                seq=await next_seq(history_id),
                                turn_id=asst_turn,
                                tool_run_id=tool_run,
                                run_id=run_id,
                                parent_ids=parent_ids
                            )
                            db_session.add(tool_result_msg)
                            await db_session.commit()
                            await db_session.refresh(tool_result_msg)

                            # Emit WebSocket event for tool result message (top-level fields only)
                            await self.emit_chat_event(session_id, history_id, 'message_received', {
                                'message_id': tool_result_msg.id,
                                'role': tool_result_msg.role,
                                'message_type': 'tool_result',
                                'status': 'complete',
                                'tool_name': tool_name,
                                'tool_args': tool_args,
                                'execution_status': 'completed',
                                'result': tool_result_msg.content_json.get('result'),
                                'executed_by': 'llm',
                                'execution_time': tool_result_msg.content_json.get('execution_time'),
                                'execution_path': 'langchain',
                                'seq': tool_result_msg.seq,
                                'turn_id': tool_result_msg.turn_id,
                                'tool_run_id': tool_result_msg.tool_run_id,
                                'run_id': tool_result_msg.run_id,
                                'parent_ids': parent_ids,
                                'timestamp': tool_result_msg.created_at.isoformat()
                            })

                        # Remove tool_name from metadata to avoid duplicate keyword argument
                        metadata = {k: v for k, v in message.metadata.items() if k != "tool_name"}
                        metadata['seq'] = tool_result_msg.seq
                        metadata['turn_id'] = tool_result_msg.turn_id
                        await event_manager.emit_tool_event(session_id, history_id, tool_name, "completed", **metadata)

                    elif message.chunk_type == "complete":
                        message.metadata = message.metadata or {}
                        # Keep original placeholder seq; finalize without changing seq
                        await message_handler.finalize_assistant_message(accumulated_text if accumulated_text else None)
                        if asst_seq is not None:
                            message.metadata['seq'] = asst_seq
                        if asst_turn is not None:
                            message.metadata['turn_id'] = asst_turn
                        await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)
                        break

                    elif message.chunk_type == "error":
                        # Handle error chunks - mark message as error and emit error event
                        await message_handler.mark_as_error(message.content)
                        await event_manager.emit_streaming_error(
                            session_id,
                            history_id,
                            message.content,
                            "provider_error",
                            asst_msg_id
                        )
                        break

            except Exception as e:
                # Handle streaming errors
                await message_handler.mark_as_error(f"Streaming error: {str(e)}")
                await message_handler.cleanup_on_error()  # Clean up on error
                await event_manager.emit_streaming_error(
                    session_id,
                    history_id,
                    f"Streaming error: {str(e)}",
                    "streaming_error",
                    asst_msg_id
                )
                await self.emit_llm_event(session_id, history_id, 'processing_failed', f"Streaming error: {str(e)}")

        except Exception as e:
            await message_handler.cleanup_on_error()
            await self.emit_llm_event(
                session_id,
                history_id,
                'processing_failed',
                f"Async processing error: {str(e)}"
            )
            self._logger.error(f"Error in _process_message_async: {e}", exc_info=True)
