import logging
from typing import Optional

from ...import db
from ....models import ChatMessage


class StreamingMessageHandler:
    """Handles streaming message creation and updates."""

    def __init__(self, session_id: int, history_id: int):
        self.session_id = session_id
        self.history_id = history_id
        self.assistant_message_id: Optional[int] = None
        self._logger = logging.getLogger(__name__)

    async def finalize_assistant_message(self, final_content: str = None, error: bool = False):
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

    async def mark_as_error(self, error_message: str):
        """Mark assistant message as error."""
        return self.finalize_assistant_message(error_message, error=True)

    async def update_content_safely(self, chunk: str) -> bool:
        """Update content with error handling, returns success status."""
        try:
            if not chunk or not isinstance(chunk, str):
                return False

            # Simple content update
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            if not asst_msg:
                return False

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
            return True

        except Exception as e:
            self._logger.error(f"Failed to update content safely: {e}", exc_info=True)
            return False

    async def ensure_message_exists(self) -> bool:
        """Ensure the assistant message exists and is accessible."""
        if not self.assistant_message_id:
            return False

        try:
            asst_msg = ChatMessage.query.get(self.assistant_message_id)
            return asst_msg is not None
        except Exception as e:
            self._logger.error(f"Failed to validate message existence: {e}", exc_info=True)
            return False

    async def cleanup_on_error(self):
        """Clean up resources and mark message as error if needed."""
        try:
            if self.assistant_message_id:
                # Mark as error if still processing
                self.mark_as_error("Processing interrupted due to error")
                self._logger.info(f"Cleaned up assistant message {self.assistant_message_id} on error")
        except Exception as e:
            self._logger.error(f"Failed to cleanup on error: {e}", exc_info=True)
