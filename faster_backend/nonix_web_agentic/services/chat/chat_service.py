import asyncio
import importlib
from datetime import datetime
import json
from typing import Any, Dict, List, AsyncGenerator, TYPE_CHECKING, Optional

from fastapi.responses import JSONResponse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from sqlalchemy import select

from nonix_web.plugin.descriptor import InjectPlugin
from nonix_web.services.base_service import BaseService, routed_service, route
from nonix_web_db import AsyncSessionLocal
from .mixins.chat_history_mixin import ChatHistoryMixin
from .mixins.chat_message_mixin import ChatMessageMixin
from .mixins.chat_session_mixin import ChatSessionMixin
from .mixins.models_and_schemas import TaskManagerHealthResponse
from .mixins.persona_chat_mixin import PersonaChatMixin
from .mixins.tool_execution_mixin import ToolExecutionMixin
from .streaming_interface import StreamingChunk
from .task_manager import ChatTaskManager
from ...llm.llm_message_utils import LCAIMessage, LCToolMessage, iter_messages
from ...models.persona import Persona

if TYPE_CHECKING:
    from ...plugin import NxWebAgenticPlugin


@routed_service("/chat", tags=["Chat"])
class ChatService(BaseService, ChatSessionMixin, ChatMessageMixin, ChatHistoryMixin, PersonaChatMixin,
                  ToolExecutionMixin):
    """Complete chat service handling session lifecycle, messaging, and tool execution.
    
    This service is composed of multiple mixins for better organization:
    - ChatSessionMixin: Session CRUD operations
    - ChatMessageMixin: Message handling and sending
    - ChatHistoryMixin: History management
    - PersonaChatMixin: Persona-related operations
    - ToolExecutionMixin: Tool execution and MCP operations
    """
    agentic_plugin: "NxWebAgenticPlugin" = InjectPlugin("agentic")

    def __init__(self, router):
        super().__init__(router)
        self._task_manager = ChatTaskManager()
        ChatMessageMixin.__init__(self)
        self._logger.info("ChatService initialized with task manager")

    async def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        room = f'chat/{session_id}/{history_id}'
        await self.send_ws_message(room, {
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

    def get_task_manager_health(self):
        return self._task_manager.get_health_status()

    def get_task_manager_stats(self):
        """Get task manager statistics for monitoring."""
        return self._task_manager.get_stats()

    @route(
        '/health/task-manager',
        methods=['GET'],
        response_model=TaskManagerHealthResponse
    )
    async def task_manager_health(self, req):
        try:
            health_status = self.get_task_manager_health()
            return health_status
        except Exception as e:
            self._logger.error(f"Failed to get task manager health: {e}", exc_info=True)
            return JSONResponse(f"Failed to get task manager health: {e}", 500)

    async def run_chat_streaming(
            self,
            provider: Any,
            mapping: Any,
            messages: List[Dict[str, Any]],
            available_tools_info: List[Dict[str, Any]],
            persona_id: int
    ) -> AsyncGenerator[StreamingChunk, None]:
        cfg: Dict[str, Any] = provider.config_json or {}
        model_name: str = mapping.model_name
        params: Dict[str, Any] = mapping.parameters_json or {}

        module_name: str = getattr(provider, 'module', '') or ''
        class_name: str = getattr(provider, 'cls', '') or ''
        # method_name: str = (getattr(provider, 'method', None) or 'invoke')

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
                    select(Persona).where(Persona.id == persona_id)
                )
                persona = persona_result.scalar_one_or_none()
                if persona:
                    persona_system_prompt = persona.system_prompt or ""

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
                        conversation_history.append(("system", content))

                # Use streaming with astream_events

                async for mode, message in iter_messages(new_agent.astream_events({
                    "chat_history": conversation_history,
                    "input": user_content
                })):
                    if mode == "start":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content="", chunk_type="ai_start")
                            initial_content = message.status.get("content", "")
                            if initial_content:
                                yield StreamingChunk(content=initial_content, chunk_type="text")
                        elif isinstance(message, LCToolMessage):
                            yield StreamingChunk(
                                content="",
                                chunk_type="tool_start",
                                metadata={
                                    "tool_name": message.status.get("tool_name", "unknown"),
                                    "args": message.status.get("input", {})
                                }
                            )

                    elif mode == "update":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content=message.status.get("content", ""), chunk_type="text")

                    elif mode == "end":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content="", chunk_type="complete", is_final=True)
                        elif isinstance(message, LCToolMessage):
                            raw_output = message.get_status("output")
                            parsed = None
                            # Normalize LangChain ToolMessage output to JSON-serializable exec_result
                            if hasattr(raw_output, 'content'):
                                content_text = raw_output.content
                                try:
                                    parsed = json.loads(content_text)
                                except Exception:
                                    parsed = {"success": False, "error": "Non-JSON tool output", "content": content_text}
                            else:
                                parsed = raw_output if isinstance(raw_output, (dict, list, str, int, float, bool, type(None))) else {"value": str(raw_output)}

                            status_val = 'success' if isinstance(parsed, dict) and parsed.get('success') is True else 'error'
                            exec_result = {"status": status_val, "result": parsed}

                            yield StreamingChunk(
                                content="",
                                chunk_type="tool_end",
                                metadata={
                                    "tool_name": message.status.get("tool_name", "unknown"),
                                    "result": exec_result
                                }
                            )

            else:
                error_message = "No user message found. Please try sending a message again."
                yield StreamingChunk(content=error_message, chunk_type="error", is_final=True)

        except Exception as exc:  # noqa: BLE001
            self._logger.error(f"Provider error: {exc}", exc_info=True)
            error_message = self._format_user_friendly_error(exc, "connection_error")
            yield StreamingChunk(content=error_message, chunk_type="error", is_final=True)

    async def run_chat_streaming_with_retry(self, provider, mapping, messages, available_tools_info, persona_id, max_retries: int = 2):
        """Run chat streaming with automatic retry for connection errors."""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                async for chunk in self.run_chat_streaming(provider, mapping, messages, available_tools_info, persona_id):
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
