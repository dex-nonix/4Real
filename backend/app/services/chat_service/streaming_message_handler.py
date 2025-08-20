from typing import Dict, Any, Optional
from ..models.chat_message import ChatMessage
from ..models.chat_history import ChatHistory
from .. import db
from .streaming_interface import StreamingChunk


class StreamingMessageHandler:
    """Handles streaming message creation and updates."""
    
    def __init__(self, session_id: int, history_id: int):
        self.session_id = session_id
        self.history_id = history_id
        self.assistant_message_id: Optional[int] = None
    
    def create_assistant_placeholder(self) -> int:
        """Create empty assistant message and return its ID."""
        asst_msg = ChatMessage(
            history_id=self.history_id,
            role='assistant',
            message_type='text',
            content_json={'type': 'text', 'text': ''},
            status='processing'
        )
        db.session.add(asst_msg)
        db.session.commit()
        
        self.assistant_message_id = asst_msg.id
        return asst_msg.id
    
    def update_assistant_content(self, chunk: str) -> str:
        """Update assistant message with new chunk."""
        if not self.assistant_message_id:
            raise ValueError("Assistant message not created yet")
        
        asst_msg = ChatMessage.query.get(self.assistant_message_id)
        if not asst_msg:
            raise ValueError(f"Assistant message {self.assistant_message_id} not found")
        
        current_content = asst_msg.content_json.get('text', '')
        new_content = current_content + chunk
        asst_msg.content_json = {'type': 'text', 'text': new_content}
        db.session.commit()
        
        return new_content
    
    def finalize_assistant_message(self, final_content: str = None):
        """Mark assistant message as complete."""
        if not self.assistant_message_id:
            raise ValueError("Assistant message not created yet")
        
        asst_msg = ChatMessage.query.get(self.assistant_message_id)
        if not asst_msg:
            raise ValueError(f"Assistant message {self.assistant_message_id} not found")
        
        # Update content if provided
        if final_content is not None:
            asst_msg.content_json = {'type': 'text', 'text': final_content}
        
        # Mark as complete
        asst_msg.status = 'complete'
        db.session.commit()
        
        return asst_msg.id
    
    def get_assistant_message_id(self) -> Optional[int]:
        """Get the current assistant message ID."""
        return self.assistant_message_id
    
    def is_assistant_message_created(self) -> bool:
        """Check if assistant message has been created."""
        return self.assistant_message_id is not None
