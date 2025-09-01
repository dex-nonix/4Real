from datetime import datetime
from typing import Dict, Any

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
        elif chunk.chunk_type == "error":
            await self.emit_streaming_error(
                session_id, 
                history_id, 
                chunk.content, 
                "provider_error", 
                message_id
            )
        elif chunk.chunk_type == "tool_start":
            tool_name = chunk.metadata.get("tool_name", "unknown")
            # Remove tool_name from metadata to avoid duplicate keyword argument
            metadata = {k: v for k, v in chunk.metadata.items() if k != "tool_name"}
            await self.emit_tool_event(session_id, history_id, tool_name, "started", **metadata)
        elif chunk.chunk_type == "tool_end":
            tool_name = chunk.metadata.get("tool_name", "unknown")
            # Remove tool_name from metadata to avoid duplicate keyword argument
            metadata = {k: v for k, v in chunk.metadata.items() if k != "tool_name"}
            await self.emit_tool_event(session_id, history_id, tool_name, "completed", **metadata)

    async def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra):
        await self.chat_service.emit_tool_event(session_id, history_id, tool_name, status, **extra)

    async def emit_llm_status_event(self, session_id: int, history_id: int, stage: str, message: str,
                                    metadata: Dict[str, Any] = None):
        await self.chat_service.emit_llm_event(session_id, history_id, stage, message)

    async def emit_streaming_error(self, session_id: int, history_id: int, error_message: str,
                                   error_type: str = "streaming_error", message_id: int = None):
        error_data = {
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': self._get_timestamp()
        }
        if message_id:
            error_data['message_id'] = message_id

        await self.chat_service.emit_chat_event(session_id, history_id, 'streaming_error', error_data)

    def _get_timestamp(self) -> str:
        return datetime.utcnow().isoformat()
