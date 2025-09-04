from typing import Protocol, TYPE_CHECKING, Any, List, Dict, AsyncGenerator

from nonix_web.utils.di import Inject

from ...llm.agentic_tool_manager import AgenticToolManager

if TYPE_CHECKING:
    from .task_manager import ChatTaskManager
    from .streaming_interface import StreamingChunk
    from nonix_web.server import NxWebServer
    from logging import Logger


class WebSocketMixinProtocol(Protocol):
    """Protocol for WebSocket event emission - Python's way of defining contracts."""

    _logger: "Logger"
    _task_manager : "ChatTaskManager"
    server: "NxWebServer"
    agentic_tool_manager: AgenticToolManager = Inject(AgenticToolManager)

    async def submit_async_task(self, func, *args, **kwargs):
        ...

    async def run_chat_streaming(
            self,
            provider: Any,
            mapping: Any,
            messages: List[Dict[str, Any]],
            available_tools_info: List[Dict[str, Any]],
            persona_id: int
    ) -> AsyncGenerator["StreamingChunk", None]:
        ...

    async def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        """Emit chat event - Protocol method."""
        ...

    async def emit_llm_event(self, session_id: int, history_id: int, stage: str, message: str) -> None:
        """Emit LLM status event - Protocol method."""
        ...

    async def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra) -> None:
        """Emit tool execution event - Protocol method."""
        ...
