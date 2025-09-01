from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from nonix_web.services.base_service import route
from nonix_web_db import AsyncSessionLocal
from .models_and_schemas import (
    MessageListResponse,
    SendMessageToHistoryRequest,
    DeleteMessageResponse,
    MessageResponse
)
from ..message_handlers import ChatMessageHandler, ToolCallMessageHandler
from ..message_type_registry import message_type_registry
from ..streaming_event_manager import StreamingEventManager
from ..streaming_interface import StreamingChunk
from ..streaming_message_handler import StreamingMessageHandler
from ..websocket_protocol import WebSocketMixinProtocol
from ....models.ai_model_mapping import AIModelMapping
from ....models.ai_provider import AIProvider
from ....models.chat_history import ChatHistory
from ....models.chat_message import ChatMessage
from ....models.chat_session import ChatSession
from ....models.persona import Persona
from ....models.tool_invocation_log import ToolInvocationLog


class ChatMessageMixin(WebSocketMixinProtocol):
    """Mixin for chat message handling and sending operations."""

    def __init__(self):
        """Initialize message type handlers."""
        # Register message type handlers (meta-types)
        message_type_registry.register('user', ChatMessageHandler())
        message_type_registry.register('tool_call', ToolCallMessageHandler())

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
            asst_msg = ChatMessage(
                history_id=history_id,
                role='assistant',
                message_type='assistant',
                content_json={'text': ''},
                status='processing'
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

            # Add system messages
            system_result = await db_session.execute(
                select(ChatMessage).where(ChatMessage.history_id == history_id, ChatMessage.role == 'system').order_by(
                    ChatMessage.created_at.asc())
            )
            system_msgs = system_result.scalars().all()
            self._logger.debug(f"Found {len(system_msgs)} system messages")
            for sm in system_msgs:
                content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
                chat_history.append({'role': 'system', 'content': content})

            # Add user and assistant messages up to current user message
            user_result = await db_session.execute(
                select(ChatMessage).where(ChatMessage.history_id == history_id,
                                          ChatMessage.id <= user_msg_id).order_by(
                    ChatMessage.created_at.asc())
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

    async def _execute_tool_call(self, persona_id: int, tool_name: str, tool_args: Dict[str, Any],
                                 history_id: int, user_msg_id: int, available_tools: Dict[str, Any]):
        """Execute tool call and return result."""
        self._logger.info(f"Executing tool '{tool_name}' for persona {persona_id}")
        self._logger.debug(f"Tool arguments: {tool_args}")

        if tool_name not in available_tools:
            self._logger.warning(f"Tool '{tool_name}' not allowed for persona {persona_id}")
            return None, f'Tool {tool_name} not allowed'

        async with AsyncSessionLocal() as db_session:
            # Log tool execution
            log = ToolInvocationLog(
                history_id=history_id,
                message_id=user_msg_id,
                tool_name=tool_name,
                input_json=tool_args,
                status='started'
            )
            db_session.add(log)
            await db_session.commit()
            await db_session.refresh(log)
            self._logger.debug(f"Tool invocation logged with ID {log.id}")

            # ✅ FIXED: Create tool_call message before execution (like ToolCallMessageHandler)
            tool_call_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='tool_call',
                content_json={
                    'tool_name': tool_name,
                    'tool_args': tool_args,
                    'executed_by': 'llm',
                    'execution_time': datetime.now(timezone.utc).isoformat(),
                    'execution_path': 'streaming'
                },
                status='complete'
            )
            db_session.add(tool_call_msg)
            await db_session.commit()
            await db_session.refresh(tool_call_msg)
            self._logger.debug(f"Tool call message {tool_call_msg.id} created")

            # Emit WebSocket event for tool call (like ToolCallMessageHandler)
            # Get session_id from the history
            history_obj = await db_session.get(ChatHistory, history_id)
            if history_obj:
                session_id = history_obj.session_id
                await self.emit_chat_event(session_id, history_id, 'message_received', {
                    'message_id': tool_call_msg.id,
                    'role': tool_call_msg.role,
                    'message_type': 'tool_call',
                    'content': tool_call_msg.content_json,
                    'timestamp': tool_call_msg.created_at.isoformat()
                })

                # Emit WebSocket event for tool execution started
                await self.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)

            # Execute tool
            self._logger.debug(f"Calling execute_tool for '{tool_name}'")
            exec_result = await self.agentic_tool_manager.execute_tool(persona_id, tool_name, tool_args)
            log.status = 'success' if exec_result.get('status') == 'success' else 'error'
            log.output_json = exec_result
            await db_session.commit()

            status = 'success' if exec_result.get('status') == 'success' else 'error'
            self._logger.info(f"Tool '{tool_name}' execution completed with status: {status}")

            # Emit WebSocket event for tool execution completed
            if 'session_id' in locals():
                await self.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)

            # Create tool result message
            tool_msg = ChatMessage(
                history_id=history_id,
                role='tool',
                message_type='tool_result',
                content_json={
                    'tool_name': tool_name,        # ✅ Standardized: snake_case
                    'tool_args': tool_args,        # ✅ Standardized: snake_case
                    'execution_status': status,    # ✅ Standardized: consistent field
                    'result': exec_result,         # ✅ Standardized: consistent field
                    'executed_by': 'llm',          # ✅ Standardized: execution context
                    'execution_time': datetime.now(timezone.utc).isoformat(),  # ✅ Standardized: timestamp
                    'execution_path': 'streaming'  # ✅ Standardized: execution path identifier
                }
            )
            db_session.add(tool_msg)
            await db_session.commit()
            await db_session.refresh(tool_msg)
            self._logger.debug(f"Tool result message {tool_msg.id} created")

            return exec_result, None

    async def _create_assistant_message(self, history_id: int, content: Dict[str, Any],
                                        status: str = 'complete') -> ChatMessage:
        """Create and save assistant message."""
        self._logger.debug(f"Creating assistant message for history {history_id} with status '{status}'")

        async with AsyncSessionLocal() as db_session:
            asst_msg = ChatMessage(
                history_id=history_id,
                role='assistant',
                message_type='assistant',
                content_json=content,
                status=status
            )
            db_session.add(asst_msg)
            await db_session.commit()
            await db_session.refresh(asst_msg)

            self._logger.info(f"Assistant message {asst_msg.id} created successfully for history {history_id}")
            return asst_msg

    async def _format_error_response(self, error_message: str, status_code: int = 400):
        """Format error response consistently."""
        return JSONResponse({'error': error_message}, status_code)

    @route(
        '/sessions/{id}/messages',
        methods=['GET'],
        response_model=MessageListResponse
    )
    async def list_messages(self, req: Request, id: int):  # noqa: A002
        """List messages from a chat session's current history."""
        try:
            async with AsyncSessionLocal() as db_session:
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

                # Get messages from current history
                if not session.current_history_id:
                    return {'data': [], 'total': 0}

                msgs = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == session.current_history_id).order_by(
                        ChatMessage.created_at.asc())
                ).scalars().all()

                return {'data': [m.to_dict() for m in msgs], 'total': len(msgs)}
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, status_code=500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/send',
        methods=['POST'],
        response_model=MessageResponse
    )
    async def send_message(
            self,
            req: Request,
            payload: SendMessageToHistoryRequest,
            session_id: int = None,
            history_id: int = None
    ):
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
                return await self._format_error_response('Session not found', 404)

            persona = session.persona
            if not persona:
                self._logger.warning(f"Session {session_id} has no persona")
                return await self._format_error_response('Session has no persona', 400)
            if not persona.is_active:
                self._logger.warning(f"Persona {persona.id} is not active")
                return await self._format_error_response('Persona is not active', 400)

            if not history_id:
                self._logger.debug(
                    f"No history_id provided, using session.current_history_id: {session.current_history_id}")
                history_id = session.current_history_id
                if not history_id:
                    self._logger.warning(f"No current history found for session {session_id}")
                    return await self._format_error_response('No current history', 400)
            else:
                self._logger.debug(f"History_id provided: {history_id}, history object: {history}")
                # Validate provided history_id belongs to session
                if not history or history.session_id != session_id:
                    self._logger.warning(f"History validation failed - history: {history}, session_id: {session_id}")
                    return await self._format_error_response('History not found or invalid', 404)

            # Get user content (object)
            user_content = payload.content
            if not user_content:
                return await self._format_error_response('content required', 400)

            # Enforce explicit meta-type from frontend (top-level message_type only)
            message_type = getattr(payload, 'message_type', None)
            if not message_type:
                return await self._format_error_response('message_type is required', 400)

            self._logger.info(f"Processing message type: {message_type}")
            self._logger.debug(f"Available message types: {message_type_registry.list_types()}")
            self._logger.debug(
                f"Handler found for type '{message_type}': {message_type_registry.has_handler(message_type)}")

            # Get handler from registry
            handler = message_type_registry.get_handler(message_type)
            self._logger.debug(f"Message handler resolved: {type(handler).__name__}")
            if not handler:
                self._logger.error(f"Unknown message type: {message_type}")
                return await self._format_error_response(f'Unknown message type: {message_type}', 400)

            result = await handler.handle(
                chat_service=self,
                session=session,
                persona=persona,
                history_id=history_id,  # ALWAYS provided (extracted or from URL)
                content=user_content
            )

            self._logger.info(f"Message processed successfully by handler, returning result")
            return JSONResponse({'data': result})

        except Exception as exc:
            self._logger.error(f"Error in send_message: {exc}", exc_info=True)
            return await self._format_error_response(str(exc), 500)

    async def submit_message_for_async_processing(
            self,
            user_msg_id: int,
            asst_msg_id: int,
            session_id: int,
            history_id: int,
            persona_id: int
    ):
        """Submit message processing to task manager for async execution."""
        try:
            # Use the task manager from the parent ChatService with session tracking
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
            self._logger.info(f"Message {user_msg_id} submitted to task manager for async processing (session: {session_id})")
            return future

        except Exception as e:
            # Log error with full stack trace
            self._logger.error(f"Failed to submit message {user_msg_id} to task manager: {e}", exc_info=True)
            # Emit error event
            await self.emit_llm_event(session_id, history_id, 'processing_failed', f'Failed to start processing: {e}')
            raise

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages/{assistant_message_id}/cancel',
        methods=['POST'],
        response_model=Dict[str, Any]
    )
    async def cancel_message_streaming(self, req: Request, session_id: int, history_id: int, assistant_message_id: int):
        """Cancel streaming for a single assistant message (per-request cancel)."""
        try:
            # Validate session and history exist and match
            session, history = await self._validate_session_history(session_id, history_id)
            if not session or not history:
                return await self._format_error_response('Session or history not found', 404)

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

            return JSONResponse({
                'message': 'Cancelled message task' if cancelled else 'No active task for message',
                'assistant_message_id': assistant_message_id,
                'cancelled': cancelled
            })
        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)

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
                        if await message_handler.update_content_safely(message.content):
                            await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)
                        else:
                            # Log error but continue processing
                            self._logger.error(f"Failed to update content for chunk: {message.content[:50]}...")

                    elif message.chunk_type == "ai_start":
                        await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)

                    elif message.chunk_type == "tool_start":
                        tool_name = message.metadata.get("tool_name", "")
                        tool_args = message.metadata.get("args", {})

                        # ✅ FIXED: Create tool_call message for LangChain tool execution
                        async with AsyncSessionLocal() as db_session:
                            # Create ToolInvocationLog for LangChain tool execution
                            log = ToolInvocationLog(
                                history_id=history_id,
                                message_id=user_msg_id,  # Use the current user message ID
                                tool_name=tool_name,
                                input_json=tool_args,
                                status='started'
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
                                status='complete'
                            )
                            db_session.add(tool_call_msg)
                            await db_session.commit()
                            await db_session.refresh(tool_call_msg)

                            # Emit WebSocket event for tool call message
                            await self.emit_chat_event(session_id, history_id, 'message_received', {
                                'message_id': tool_call_msg.id,
                                'role': tool_call_msg.role,
                                'message_type': 'tool_call',
                                'content': tool_call_msg.content_json,
                                'timestamp': tool_call_msg.created_at.isoformat()
                            })

                        await event_manager.emit_tool_event(session_id, history_id, tool_name, "started", args=tool_args)

                    elif message.chunk_type == "tool_end":
                        tool_name = message.metadata.get("tool_name", "")
                        tool_args = message.metadata.get("args", {})

                        # ✅ FIXED: Create tool_result message for LangChain tool execution
                        # Note: LangChain may not provide detailed result in metadata, so we create a basic message
                        async with AsyncSessionLocal() as db_session:
                            # Update ToolInvocationLog with completion status
                            # Find the log entry created during tool_start
                            log_result = await db_session.execute(
                                select(ToolInvocationLog).where(
                                    ToolInvocationLog.history_id == history_id,
                                    ToolInvocationLog.tool_name == tool_name,
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
                                content_json={
                                    'tool_name': tool_name,
                                    'tool_args': tool_args,
                                    'execution_status': 'completed',  # LangChain handled the execution
                                    'result': message.metadata.get("result", {"status": "completed"}),
                                    'executed_by': 'llm',
                                    'execution_time': datetime.now(timezone.utc).isoformat(),
                                    'execution_path': 'langchain'
                                }
                            )
                            db_session.add(tool_result_msg)
                            await db_session.commit()
                            await db_session.refresh(tool_result_msg)

                            # Emit WebSocket event for tool result message
                            await self.emit_chat_event(session_id, history_id, 'message_received', {
                                'message_id': tool_result_msg.id,
                                'role': tool_result_msg.role,
                                'message_type': 'tool_result',
                                'content': tool_result_msg.content_json,
                                'timestamp': tool_result_msg.created_at.isoformat()
                            })

                        await event_manager.emit_tool_event(session_id, history_id, tool_name, "completed", **message.metadata)

                    elif message.chunk_type == "complete":
                        await message_handler.finalize_assistant_message(accumulated_text if accumulated_text else None)
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

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages',
        methods=['GET'],
        response_model=MessageListResponse
    )
    async def list_history_messages(self, req: Request, session_id: int, history_id: int):
        """Get messages from a specific history within a session."""
        try:
            # Validate session and history
            session, history = await self._validate_session_history(session_id, history_id)
            if not session:
                return await self._format_error_response('Session not found or inactive', 404)
            if not history:
                return await self._format_error_response('History not found', 404)

            async with AsyncSessionLocal() as db_session:
                result = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == history_id).order_by(
                        ChatMessage.created_at.asc())
                )
                msgs = result.scalars().all()
                return JSONResponse({'data': [m.to_dict() for m in msgs], 'total': len(msgs)})
        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages',
        methods=['DELETE'],
        response_model=DeleteMessageResponse
    )
    async def clear_history_messages(self, req: Request, session_id: int, history_id: int):
        """Clear all messages from a specific history."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Verify session exists and is active
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    return await self._format_error_response('Session not found or inactive', 404)

                # Verify history exists and belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    return await self._format_error_response('History not found', 404)

                # Count messages before deletion
                messages_result = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == history_id)
                )
                messages = messages_result.scalars().all()
                deleted_count = len(messages)

                # Delete all messages in the history
                for message in messages:
                    await db_session.delete(message)

                # Reset history message count
                history.message_count = 0

                await db_session.commit()

                return JSONResponse({
                    'message': f'Successfully cleared {deleted_count} messages from history',
                    'deleted_count': deleted_count
                })

        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages/{message_id}',
        methods=['DELETE'],
        response_model=DeleteMessageResponse
    )
    async def delete_message(self, req: Request, session_id: int, history_id: int, message_id: int):
        """Delete a specific message from a history."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Verify session exists and is active
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    return await self._format_error_response('Session not found or inactive', 404)

                # Verify history exists and belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    return await self._format_error_response('History not found', 404)

                # Find and delete the specific message
                message = (await db_session.execute(
                    select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.history_id == history_id)
                )).scalar_one_or_none()

                if not message:
                    return await self._format_error_response('Message not found', 404)

                # Store message ID before deletion for response
                deleted_message_id = message.id

                # Delete the message
                await db_session.delete(message)

                # Update history message count
                history.message_count = max(0, history.message_count - 1)

                await db_session.commit()

                return JSONResponse({
                    'message': 'Message deleted successfully',
                    'deleted_message_id': deleted_message_id
                })

        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)


    @route(
        '/sessions/{session_id}/retry',
        methods=['POST'],
        response_model=Dict[str, Any]
    )
    async def retry_last_message(self, req: Request, session_id: int):
        """Retry the last user message in a session."""
        try:
            # Validate session exists
            session, history = await self._validate_session_history(session_id)
            if not session:
                return await self._format_error_response('Session not found or inactive', 404)

            # Get the last user message
            last_user_msg = await self._get_last_user_message(session_id)
            if not last_user_msg:
                return await self._format_error_response('No user messages to retry', 400)

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

            return JSONResponse({
                'message': 'Message retry initiated',
                'session_id': session_id,
                'user_message_id': last_user_msg.id,
                'assistant_message_id': asst_msg.id,
                'status': 'processing'
            })

        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)

    async def _cancel_session_streaming(self, session_id: int) -> bool:
        """Cancel active streaming for a specific session."""
        try:
            # Get the task manager from the main service
            task_manager = getattr(self, '_task_manager', None)
            if not task_manager:
                self._logger.warning("Task manager not available for cancellation")
                return False

            # Use the enhanced session-specific cancellation
            cancelled_count = await task_manager.cancel_session_tasks(session_id)
            
            self._logger.info(f"Cancelled {cancelled_count} active tasks for session {session_id}")
            return cancelled_count > 0

        except Exception as e:
            self._logger.error(f"Failed to cancel streaming for session {session_id}: {e}", exc_info=True)
            return False

    async def _get_last_user_message(self, session_id: int) -> ChatMessage | None:
        """Get the last user message from a session."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Get the last user message from any history in this session
                result = await db_session.execute(
                    select(ChatMessage)
                    .join(ChatHistory, ChatMessage.history_id == ChatHistory.id)
                    .where(ChatHistory.session_id == session_id, ChatMessage.role == 'user')
                    .order_by(ChatMessage.created_at.desc())
                    .limit(1)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            self._logger.error(f"Failed to get last user message for session {session_id}: {e}", exc_info=True)
            return None

    async def _get_last_user_message_content(self, session_id: int) -> Dict[str, Any] | None:
        """Get the last user message content for retry functionality."""
        try:
            last_msg = await self._get_last_user_message(session_id)
            if not last_msg:
                return None
                
            # Extract the message content in the format expected by the frontend
            content = last_msg.content_json or {}
            if isinstance(content, dict):
                # If it's already a dict, return as is
                return {
                    'type': content.get('type', 'text'),
                    'text': content.get('text', str(content))
                }
            else:
                # If it's a string or other format, wrap it
                return {
                    'type': 'text',
                    'text': str(content)
                }
                
        except Exception as e:
            self._logger.error(f"Failed to get last user message content for session {session_id}: {e}", exc_info=True)
            return None

    @route(
        '/sessions/{session_id}/last-message',
        methods=['GET'],
        response_model=Dict[str, Any]
    )
    async def get_last_user_message(self, req: Request, session_id: int):
        """Get the last user message content for retry functionality."""
        try:
            # Validate session exists
            session, _ = await self._validate_session_history(session_id)
            if not session:
                return await self._format_error_response('Session not found or inactive', 404)

            # Get the last user message content
            last_message_content = await self._get_last_user_message_content(session_id)
            if not last_message_content:
                return await self._format_error_response('No user messages found', 404)

            return JSONResponse({
                'session_id': session_id,
                'last_message': last_message_content,
                'can_retry': True
            })

        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)
