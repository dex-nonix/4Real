"""
Chat Service Module

This module provides a modular chat service implementation split into logical mixins:
- ChatSessionMixin: Session management operations
- ChatMessageMixin: Message handling and sending
- ChatHistoryMixin: History management
- PersonaChatMixin: Persona-related operations
- ToolExecutionMixin: Tool execution and MCP operations
- WebSocketProtocol: WebSocket event emission contract

The main ChatService class inherits from all mixins to provide complete functionality.
"""

from .chat_service import ChatService
from .chat_session_mixin import ChatSessionMixin
from .chat_message_mixin import ChatMessageMixin
from .chat_history_mixin import ChatHistoryMixin
from .persona_chat_mixin import PersonaChatMixin
from .tool_execution_mixin import ToolExecutionMixin
from .websocket_protocol import WebSocketProtocol

__all__ = [
    'ChatService',
    'ChatSessionMixin',
    'ChatMessageMixin',
    'ChatHistoryMixin',
    'PersonaChatMixin',
    'ToolExecutionMixin',
    'WebSocketProtocol'
]
