from typing import Dict, Any
from datetime import datetime
from .streaming_interface import StreamingChunk


class StreamingEventManager:
    """Manages streaming event emission."""

    def __init__(self, chat_service):
        self.chat_service = chat_service

    async def emit_chunk_event(self, session_id: int, history_id: int, chunk: StreamingChunk, message_id: int):
        """Emit chunk event via WebSocket."""
        if chunk.chunk_type == "text":
            await self.chat_service.emit_chat_event(session_id, history_id, 'assistant_message_chunk', {
                'message_id': message_id,
                'chunk': chunk.content,
                'metadata': chunk.metadata,
                'is_final': chunk.is_final
            })
        elif chunk.chunk_type == "ai_start":
            await self.chat_service.emit_chat_event(session_id, history_id, 'assistant_message_started', {
                'message_id': message_id,
                'status': 'streaming',
                'metadata': chunk.metadata
            })
        elif chunk.chunk_type == "complete":
            await self.chat_service.emit_chat_event(session_id, history_id, 'assistant_message_complete', {
                'message_id': message_id,
                'status': 'complete',
                'metadata': chunk.metadata
            })
        elif chunk.chunk_type == "tool_start":
            await self.emit_tool_event(session_id, history_id,
                                       chunk.metadata.get("tool_name", "unknown"), "started",
                                       chunk.metadata)
        elif chunk.chunk_type == "tool_end":
            await self.emit_tool_event(session_id, history_id,
                                       chunk.metadata.get("tool_name", "unknown"), "completed",
                                       chunk.metadata)

    async def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra):
        """Emit tool execution event."""
        # Pass all extra data as keyword arguments to match ChatService.emit_tool_event signature
        await self.chat_service.emit_tool_event(session_id, history_id, tool_name, status, **extra)

    async def emit_llm_status_event(self, session_id: int, history_id: int, stage: str, message: str,
                                    metadata: Dict[str, Any] = None):
        """Emit LLM status event."""
        # Call emit_llm_event with correct parameters (stage and message only)
        await self.chat_service.emit_llm_event(session_id, history_id, stage, message)

    async def emit_streaming_error(self, session_id: int, history_id: int, error_message: str,
                                   error_type: str = "streaming_error", message_id: int = None):
        """Emit streaming error event."""
        error_data = {
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': self._get_timestamp()
        }
        if message_id:
            error_data['message_id'] = message_id

        await self.chat_service.emit_chat_event(session_id, history_id, 'streaming_error', error_data)

    async def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
