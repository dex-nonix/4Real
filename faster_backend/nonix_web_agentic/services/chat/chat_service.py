import importlib
from datetime import datetime
from typing import Any, Dict, List, AsyncGenerator

from fastapi.responses import JSONResponse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from nonix_web.plugin.descriptor import InjectPlugin
from nonix_web.services.base_service import BaseService, routed_service, route
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
    agentic_plugin: NxWebAgenticPlugin = InjectPlugin("agentic")

    def __init__(self, server, router):
        super().__init__(server, router)
        self._task_manager = ChatTaskManager()
        ChatMessageMixin.__init__(self)
        self._logger.info("ChatService initialized with task manager")

    async def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        room = f'chat/{session_id}/{history_id}'
        self._logger.debug(f"Emitting chat event: room={room}, event={event}, data={data}")
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
            yield StreamingChunk(content=f'Provider import error: {exc}', chunk_type="complete", is_final=True)
            return

        try:
            client = client_cls(**kwargs)

            # Create LangChain tools (can be empty list if no tools)
            langchain_tools = []
            if available_tools_info is not None:
                langchain_tools = self.agentic_plugin.agentic_tool_registry.create_langchain_tools(
                    persona_id,
                    available_tools_info
                )
                self._logger.info(f"🔧 Created {len(langchain_tools)} LangChain tools for persona {persona_id}")

            persona = Persona.query.filter_by(id=persona_id).first()
            persona_system_prompt = persona.system_prompt if persona else ""

            template_messages = [
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
            # Create the ChatPromptTemplate with persona system prompt
            if persona_system_prompt:
                template_messages.insert(0, ("system", persona_system_prompt), )
            chat_prompt = ChatPromptTemplate.from_messages(template_messages)

            agent = create_react_agent(client, langchain_tools)

            self._logger.info(f"🔧 Created ReAct agent with {len(langchain_tools)} tools")

            # Chain the prompt with the agent
            new_agent = chat_prompt | agent

            # Get the last user message
            last_user_msg = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
            if last_user_msg:
                user_content = last_user_msg.get('content', '')
                if isinstance(user_content, dict):
                    user_content = user_content.get('text', str(user_content))

                # Convert messages to string for agent
                conversation_history = []
                for m in messages:
                    role = m.get('role')
                    content = m.get('content')
                    if isinstance(content, dict):
                        content = content.get('text', str(content))
                    if role == 'user':
                        conversation_history.append(f"Human: {content}")
                    elif role == 'assistant':
                        conversation_history.append(f"Assistant: {content}")
                    elif role == 'system':
                        conversation_history.append(f"System: {content}")

                # Use streaming with astream_events

                async for mode, message in iter_messages(new_agent.astream_events({
                    "chat_history": conversation_history,
                    "input": user_content
                })):
                    if mode == "start":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content="", chunk_type="ai_start")
                        elif isinstance(message, LCToolMessage):
                            yield StreamingChunk(
                                content="",
                                chunk_type="tool_start",
                                metadata={"tool_name": message.status.get("tool_name", "unknown")}
                            )

                    elif mode == "update":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content=message.status.get("content", ""), chunk_type="text")

                    elif mode == "end":
                        if isinstance(message, LCAIMessage):
                            yield StreamingChunk(content="", chunk_type="complete", is_final=True)
                        elif isinstance(message, LCToolMessage):
                            yield StreamingChunk(
                                content="",
                                chunk_type="tool_end",
                                metadata={"tool_name": message.status.get("tool_name", "unknown")}
                            )

            else:
                yield StreamingChunk(content="No user message found", chunk_type="complete", is_final=True)

        except Exception as exc:  # noqa: BLE001
            self._logger.error(f"Provider error: {exc}", exc_info=True)
            yield StreamingChunk(content=f'Provider error: {exc}', chunk_type="complete", is_final=True)
