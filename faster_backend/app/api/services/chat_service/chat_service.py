import logging
from datetime import datetime

from fastapi.responses import JSONResponse

from .mixins.chat_history_mixin import ChatHistoryMixin
from .mixins.chat_message_mixin import ChatMessageMixin
from .mixins.chat_session_mixin import ChatSessionMixin
from .mixins.persona_chat_mixin import PersonaChatMixin
from .mixins.tool_execution_mixin import ToolExecutionMixin
from .task_manager import ChatTaskManager
from ...service_router.base_service import BaseService
from ...service_router.decorators import expose


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

    def __init__(self, app):
        """Initialize chat service with task manager."""
        super().__init__()

        # Initialize task manager
        self.app = app
        self._task_manager = ChatTaskManager()

        # Initialize mixins
        ChatMessageMixin.__init__(self)

        # Log initialization
        self._logger = logging.getLogger(__name__)
        self._logger.info("ChatService initialized with task manager")

    async def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        """IMPLEMENT: Emit chat event using BaseService method."""
        room = f'chat/{session_id}/{history_id}'
        self._logger.debug(f"Emitting chat event: room={room}, event={event}, data={data}")
        await self.send_message(room, {
            'event': event,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def emit_llm_event(self, session_id: int, history_id: int, stage: str, message: str) -> None:
        """IMPLEMENT: Emit LLM status event."""
        await self.emit_chat_event(session_id, history_id, 'llm_status', {
            'stage': stage,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra) -> None:
        """IMPLEMENT: Emit tool execution event."""
        await self.emit_chat_event(session_id, history_id, 'tool_status', {
            'tool_name': tool_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            **extra
        })

    async def submit_async_task(self, func, *args, **kwargs):
        """Submit a task to the task manager for async execution."""
        try:
            # Submit task (ChatTaskManager handles both async and sync functions)
            future = await self._task_manager.submit_task(func, *args, **kwargs)
            self._logger.debug(f"Task submitted to task manager: {func.__name__}")
            return future
        except Exception as e:
            self._logger.error(f"Failed to submit task to task manager: {e}", exc_info=True)
            raise

    async def get_task_manager_health(self):
        """Get task manager health status for monitoring."""
        return await self._task_manager.get_health_status()

    async def get_task_manager_stats(self):
        """Get task manager statistics for monitoring."""
        return await self._task_manager.get_stats()

    @expose(
        '/health/task-manager',
        methods=['GET'],
        status_codes={200: 'OK'},
        response_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "stats": {
                    "type": "object",
                    "properties": {
                        "active_tasks": {"type": "integer"},
                        "max_concurrent_tasks": {"type": "integer"},
                        "utilization": {"type": "string"},
                        "failure_rate": {"type": "string"},
                        "total_submissions": {"type": "integer"},
                        "last_activity": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def task_manager_health(self, req):
        """Get task manager health status for monitoring."""
        try:
            health_status = await self.get_task_manager_health()
            return health_status
        except Exception as e:
            self._logger.error(f"Failed to get task manager health: {e}", exc_info=True)
            return JSONResponse(f"Failed to get task manager health: {e}", 500)
