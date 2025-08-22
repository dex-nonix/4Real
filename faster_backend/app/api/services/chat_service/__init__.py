"""
Chat Service Module

This module provides a modular chat service implementation split into logical mixins:
- ChatSessionMixin: Session management operations
- ChatMessageMixin: Message handling and sending
- ChatHistoryMixin: History management
- PersonaChatMixin: Persona-related operations
- ToolExecutionMixin: Tool execution and MCP operations
- WebSocketMixinProtocol: WebSocket event emission contract

The main ChatService class inherits from all mixins to provide complete functionality.
"""

from backend.app.services.chat_service.mixins.chat_history_mixin import ChatHistoryMixin
from backend.app.services.chat_service.mixins.chat_message_mixin import ChatMessageMixin
from .chat_service import ChatService
from backend.app.services.chat_service.mixins.chat_session_mixin import ChatSessionMixin
from backend.app.services.chat_service.mixins.persona_chat_mixin import PersonaChatMixin
from backend.app.services.chat_service.mixins.tool_execution_mixin import ToolExecutionMixin
from .websocket_protocol import WebSocketMixinProtocol

__all__ = [
    'ChatService',
    'ChatSessionMixin',
    'ChatMessageMixin',
    'ChatHistoryMixin',
    'PersonaChatMixin',
    'ToolExecutionMixin',
    'WebSocketMixinProtocol'
]
