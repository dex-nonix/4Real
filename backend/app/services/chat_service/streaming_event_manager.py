from typing import Dict, Any
from .streaming_interface import StreamingChunk


class StreamingEventManager:
    """Manages streaming event emission."""
    
    def __init__(self, chat_service):
        self.chat_service = chat_service
    
    def emit_chunk_event(self, session_id: int, history_id: int, chunk: StreamingChunk):
        """Emit chunk event via WebSocket."""
        if chunk.chunk_type == "text":
            self.chat_service.emit_chat_event(session_id, history_id, 'assistant_message_chunk', {
                'chunk': chunk.content,
                'metadata': chunk.metadata,
                'is_final': chunk.is_final
            })
        elif chunk.chunk_type == "ai_start":
            self.chat_service.emit_chat_event(session_id, history_id, 'assistant_message_started', {
                'status': 'streaming',
                'metadata': chunk.metadata
            })
        elif chunk.chunk_type == "complete":
            self.chat_service.emit_chat_event(session_id, history_id, 'assistant_message_complete', {
                'status': 'complete',
                'metadata': chunk.metadata
            })
        elif chunk.chunk_type == "tool_start":
            self.emit_tool_event(session_id, history_id, 
                               chunk.metadata.get("tool_name", "unknown"), "started", 
                               chunk.metadata)
        elif chunk.chunk_type == "tool_end":
            self.emit_tool_event(session_id, history_id, 
                               chunk.metadata.get("tool_name", "unknown"), "completed", 
                               chunk.metadata)
    
    def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, metadata: Dict[str, Any] = None):
        """Emit tool execution event."""
        event_data = {
            'tool_name': tool_name,
            'status': status,
            'timestamp': self._get_timestamp()
        }
        
        if metadata:
            event_data.update(metadata)
        
        self.chat_service.emit_tool_event(session_id, history_id, tool_name, status, **event_data)
    
    def emit_llm_status_event(self, session_id: int, history_id: int, stage: str, message: str, metadata: Dict[str, Any] = None):
        """Emit LLM status event."""
        event_data = {
            'stage': stage,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        
        if metadata:
            event_data.update(metadata)
        
        self.chat_service.emit_llm_event(session_id, history_id, stage, message)
    
    def emit_streaming_error(self, session_id: int, history_id: int, error_message: str, error_type: str = "streaming_error"):
        """Emit streaming error event."""
        self.chat_service.emit_chat_event(session_id, history_id, 'streaming_error', {
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': self._get_timestamp()
        })
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
