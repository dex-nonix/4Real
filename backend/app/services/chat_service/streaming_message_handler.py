from typing import Dict, Any, Optional
import logging

from ...models.chat_message import ChatMessage
from ... import db


class StreamingMessageHandler:
    """Handles streaming message creation and updates."""
    
    def __init__(self, session_id: int, history_id: int):
        self.session_id = session_id
        self.history_id = history_id
        self.assistant_message_id: Optional[int] = None
        self._logger = logging.getLogger(__name__)
    
    def create_assistant_placeholder(self) -> int:
        """Create empty assistant message and return its ID."""
        try:
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
            self._logger.info(f"Created assistant message placeholder: {asst_msg.id}")
            return asst_msg.id
            
        except Exception as e:
            db.session.rollback()
            self._logger.error(f"Failed to create assistant message placeholder: {e}", exc_info=True)
            raise
    
    def update_assistant_content(self, chunk: str) -> str:
        """Update assistant message with new chunk."""
        if not self.assistant_message_id:
            raise ValueError("Assistant message not created yet")
        
        try:
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            if not asst_msg:
                raise ValueError(f"Assistant message {self.assistant_message_id} not found")
            
            # Handle different content types
            current_content_json = asst_msg.content_json or {}
            if isinstance(current_content_json, dict):
                current_text = current_content_json.get('text', '')
            else:
                current_text = str(current_content_json)
            
            new_text = current_text + chunk
            new_content_json = {'type': 'text', 'text': new_text}
            
            asst_msg.content_json = new_content_json
            db.session.commit()
            
            self._logger.debug(f"Updated assistant message {self.assistant_message_id} with chunk: {chunk[:50]}...")
            return new_text
            
        except Exception as e:
            db.session.rollback()
            self._logger.error(f"Failed to update assistant message content: {e}", exc_info=True)
            raise
    
    def finalize_assistant_message(self, final_content: str = None, error: bool = False):
        """Mark assistant message as complete or error."""
        if not self.assistant_message_id:
            raise ValueError("Assistant message not created yet")
        
        try:
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            if not asst_msg:
                raise ValueError(f"Assistant message {self.assistant_message_id} not found")
            
            # Update content if provided
            if final_content is not None:
                if error:
                    # For errors, store error message in content
                    asst_msg.content_json = {
                        'type': 'error', 
                        'text': final_content,
                        'error': True
                    }
                    asst_msg.status = 'error'
                else:
                    # For normal completion, update with final content
                    asst_msg.content_json = {'type': 'text', 'text': final_content}
                    asst_msg.status = 'complete'
            else:
                # No content provided, just mark as complete
                asst_msg.status = 'complete' if not error else 'error'
            
            db.session.commit()
            
            status = 'error' if error else 'complete'
            self._logger.info(f"Finalized assistant message {self.assistant_message_id} with status: {status}")
            return asst_msg.id
            
        except Exception as e:
            db.session.rollback()
            self._logger.error(f"Failed to finalize assistant message: {e}", exc_info=True)
            raise
    
    def mark_as_error(self, error_message: str):
        """Mark assistant message as error."""
        return self.finalize_assistant_message(error_message, error=True)
    
    def get_assistant_message_id(self) -> Optional[int]:
        """Get the current assistant message ID."""
        return self.assistant_message_id
    
    def is_assistant_message_created(self) -> bool:
        """Check if assistant message has been created."""
        return self.assistant_message_id is not None
    
    def get_message_status(self) -> Optional[str]:
        """Get the current status of the assistant message."""
        if not self.assistant_message_id:
            return None
        
        try:
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            return asst_msg.status if asst_msg else None
        except Exception as e:
            self._logger.error(f"Failed to get message status: {e}", exc_info=True)
            return None
    
    def validate_message_exists(self) -> bool:
        """Validate that the assistant message still exists in database."""
        if not self.assistant_message_id:
            return False
        
        try:
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            return asst_msg is not None
        except Exception as e:
            self._logger.error(f"Failed to validate message existence: {e}", exc_info=True)
            return False
    
    def get_current_content(self) -> str:
        """Get the current content text from the assistant message."""
        if not self.assistant_message_id:
            return ""
        
        try:
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            if not asst_msg:
                return ""
            
            content_json = asst_msg.content_json or {}
            if isinstance(content_json, dict):
                return content_json.get('text', '')
            else:
                return str(content_json)
                
        except Exception as e:
            self._logger.error(f"Failed to get current content: {e}", exc_info=True)
            return ""
    
    def update_content_safely(self, chunk: str) -> bool:
        """Update content with error handling, returns success status."""
        try:
            # Validate chunk content first
            if not self.validate_chunk_content(chunk):
                self._logger.warning(f"Invalid chunk content: {chunk[:100] if chunk else 'None'}...")
                return False
            
            # Sanitize content before updating
            sanitized_chunk = self.sanitize_content(chunk)
            if sanitized_chunk != chunk:
                self._logger.info(f"Content sanitized: {len(chunk)} -> {len(sanitized_chunk)} characters")
            
            # Update with sanitized content
            self.update_assistant_content(sanitized_chunk)
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to update content safely: {e}", exc_info=True)
            return False
    
    def check_database_connection(self) -> bool:
        """Check if database connection is available."""
        try:
            # Try a simple query to test connection
            db.session.execute("SELECT 1")
            return True
        except Exception as e:
            self._logger.error(f"Database connection check failed: {e}", exc_info=True)
            return False
    
    def ensure_message_exists(self) -> bool:
        """Ensure the assistant message exists and is accessible."""
        if not self.assistant_message_id:
            return False
        
        if not self.validate_message_exists():
            self._logger.warning(f"Assistant message {self.assistant_message_id} no longer exists")
            return False
        
        return True
    
    def validate_chunk_content(self, chunk: str) -> bool:
        """Validate chunk content before processing."""
        if chunk is None:
            return False
        
        if not isinstance(chunk, str):
            return False
        
        # Check for reasonable length (prevent extremely long chunks)
        if len(chunk) > 10000:  # 10KB limit per chunk
            self._logger.warning(f"Chunk too long: {len(chunk)} characters")
            return False
        
        return True
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content to prevent injection or corruption."""
        if not content:
            return ""
        
        # Remove null bytes and other problematic characters
        sanitized = content.replace('\x00', '')
        
        # Limit length to prevent database issues
        max_length = 50000  # 50KB limit
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            self._logger.warning(f"Content truncated from {len(content)} to {max_length} characters")
        
        return sanitized
    
    def cleanup_on_error(self):
        """Clean up resources and mark message as error if needed."""
        try:
            if self.assistant_message_id and self.validate_message_exists():
                # Check current status
                current_status = self.get_message_status()
                if current_status == 'processing':
                    # Mark as error if still processing
                    self.mark_as_error("Processing interrupted due to error")
                    self._logger.info(f"Cleaned up assistant message {self.assistant_message_id} on error")
        except Exception as e:
            self._logger.error(f"Failed to cleanup on error: {e}", exc_info=True)
    
    def recover_from_error(self) -> bool:
        """Attempt to recover from error state."""
        try:
            if not self.assistant_message_id:
                return False
            
            if not self.validate_message_exists():
                return False
            
            current_status = self.get_message_status()
            if current_status == 'error':
                # Try to reset to processing state
                asst_msg = ChatMessage.query.get(self.assistant_message_id)
                if asst_msg:
                    asst_msg.status = 'processing'
                    db.session.commit()
                    self._logger.info(f"Recovered assistant message {self.assistant_message_id} from error state")
                    return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Failed to recover from error: {e}", exc_info=True)
            return False
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get a summary of the current message content and status."""
        try:
            if not self.assistant_message_id:
                return {"error": "No assistant message ID"}
            
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            if not asst_msg:
                return {"error": "Message not found"}
            
            content_json = asst_msg.content_json or {}
            current_text = content_json.get('text', '') if isinstance(content_json, dict) else str(content_json)
            
            return {
                "message_id": self.assistant_message_id,
                "status": asst_msg.status,
                "content_length": len(current_text),
                "content_preview": current_text[:100] + "..." if len(current_text) > 100 else current_text,
                "created_at": asst_msg.created_at.isoformat() if asst_msg.created_at else None,
                "updated_at": asst_msg.updated_at.isoformat() if asst_msg.updated_at else None
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get content summary: {e}", exc_info=True)
            return {"error": str(e)}
