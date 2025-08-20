from typing import Protocol
from datetime import datetime
import logging


class WebSocketProtocol(Protocol):
    """Protocol for WebSocket event emission - Python's way of defining contracts."""
    
    @property
    def _logger(self) -> logging.Logger:
        """Get logger from parent ChatService."""
        ...
    
    def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        """Emit chat event - Protocol method."""
        ...
    
    def emit_llm_event(self, session_id: int, history_id: int, stage: str, message: str) -> None:
        """Emit LLM status event - Protocol method."""
        ...
    
    def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra) -> None:
        """Emit tool execution event - Protocol method."""
        ...
