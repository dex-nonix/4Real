from typing import Any, Callable, Dict
from abc import ABC, abstractmethod

class MessageTypeHandler(ABC):
    """Abstract base class for message type handlers."""

    @abstractmethod
    def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a message of this type.

        Args:
            chat_service: ChatService instance for emit methods
            session: Session object
            persona: Persona object (MANDATORY DIRECT PARAMETER!)
            history_id: History ID (ALWAYS provided - extracted or from URL)
            content: Message content object (MANDATORY!)
        """
        pass

class MessageTypeRegistry:
    """Dynamic registry for message type handlers."""

    def __init__(self):
        self._handlers: Dict[str, MessageTypeHandler] = {}

    def register(self, message_type: str, handler: MessageTypeHandler) -> None:
        """Register a handler for a message type."""
        self._handlers[message_type] = handler
        print(f"Registered message type handler: {message_type}")

    def get_handler(self, message_type: str) -> MessageTypeHandler:
        """Get handler for message type."""
        return self._handlers.get(message_type)

    def has_handler(self, message_type: str) -> bool:
        """Check if a handler exists for the message type."""
        return message_type in self._handlers

    def list_types(self) -> list[str]:
        """List all registered message types."""
        return list(self._handlers.keys())

# Global registry instance
message_type_registry = MessageTypeRegistry()
