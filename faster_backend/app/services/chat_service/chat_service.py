from __future__ import annotations

import logging
from asyncio import iscoroutinefunction
from datetime import datetime

from flask import jsonify

from .mixins.chat_history_mixin import ChatHistoryMixin
from .mixins.chat_message_mixin import ChatMessageMixin
from .mixins.chat_session_mixin import ChatSessionMixin
from .mixins.persona_chat_mixin import PersonaChatMixin
from .mixins.tool_execution_mixin import ToolExecutionMixin
from .thread_pool_manager import ChatThreadPoolManager
from ...api.service_router.base_service import BaseService
from ...api.service_router.decorators import expose


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
        """Initialize chat service with thread pool manager."""
        super().__init__()

        # Initialize thread pool manager
        self.app = app
        self._thread_pool = ChatThreadPoolManager(app)

        # Initialize mixins
        ChatMessageMixin.__init__(self)

        # Log initialization
        self._logger = logging.getLogger(__name__)
        self._logger.info("ChatService initialized with thread pool manager")

    async def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        """IMPLEMENT: Emit chat event using BaseService method."""
        channel = f'chat/{session_id}/{history_id}'
        self._logger.debug(f"Emitting chat event: channel={channel}, event={event}, data={data}")
        await self.send_to_channel(channel, event, data)

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
        """Submit a task to the thread pool for async execution."""
        try:
            # Check if function is async and use appropriate method
            if iscoroutinefunction(func):
                future = await self._thread_pool.submit_async_task(func, *args, **kwargs)
            else:
                future = await self._thread_pool.submit_task(func, *args, **kwargs)
            self._logger.debug(f"Task submitted to thread pool: {func.__name__}")
            return future
        except Exception as e:
            self._logger.error(f"Failed to submit task to thread pool: {e}", exc_info=True)
            raise

    async def get_thread_pool_health(self):
        """Get thread pool health status for monitoring."""
        return await self._thread_pool.get_health_status()

    async def get_thread_pool_stats(self):
        """Get thread pool statistics for monitoring."""
        return await self._thread_pool.get_stats()

    @expose(
        '/health/thread-pool',
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
                        "thread_pool_size": {"type": "integer"},
                        "utilization": {"type": "string"},
                        "failure_rate": {"type": "string"},
                        "total_submissions": {"type": "integer"},
                        "last_activity": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def thread_pool_health(self, req):
        """Get thread pool health status for monitoring."""
        try:
            health_status = await self.get_thread_pool_health()
            return jsonify(health_status)
        except Exception as e:
            self._logger.error(f"Failed to get thread pool health: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
