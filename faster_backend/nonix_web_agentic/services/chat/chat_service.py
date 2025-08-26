from datetime import datetime

from fastapi.responses import JSONResponse

from nonix_web.services.base_service import BaseService, routed_service, route
from .mixins.chat_history_mixin import ChatHistoryMixin
from .mixins.chat_message_mixin import ChatMessageMixin
from .mixins.chat_session_mixin import ChatSessionMixin
from .mixins.models_and_schemas import TaskManagerHealthResponse
from .mixins.persona_chat_mixin import PersonaChatMixin
from .mixins.tool_execution_mixin import ToolExecutionMixin
from .task_manager import ChatTaskManager


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

    def __init__(self, app, router):
        super().__init__(app, router)
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
