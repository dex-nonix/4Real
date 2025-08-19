from __future__ import annotations

from flask import jsonify, Request

from ...decorators import expose, expose_ws
from ... import db
from ...models.chat_session import ChatSession
from ...models.chat_message import ChatMessage
from ...models.chat_history import ChatHistory
from ...models.persona import Persona
from ..llm_client import run_chat
from ..tool_runtime import build_persona_tool_map, execute_tool, list_persona_tools
from ..base_api_service import BaseApiService

# Import all mixins
from .chat_session_mixin import ChatSessionMixin
from .chat_message_mixin import ChatMessageMixin
from .chat_history_mixin import ChatHistoryMixin
from .persona_chat_mixin import PersonaChatMixin
from .tool_execution_mixin import ToolExecutionMixin


class ChatService(BaseApiService, ChatSessionMixin, ChatMessageMixin, ChatHistoryMixin, PersonaChatMixin, ToolExecutionMixin):
    """Complete chat service handling session lifecycle, messaging, and tool execution.
    
    This service is composed of multiple mixins for better organization:
    - ChatSessionMixin: Session CRUD operations
    - ChatMessageMixin: Message handling and sending
    - ChatHistoryMixin: History management
    - PersonaChatMixin: Persona-related operations
    - ToolExecutionMixin: Tool execution and MCP operations
    """
    
    @expose_ws('chat/{session_id}/{history_id}')
    def chat_channel(self, data: dict, session_id: int, history_id: int):
        """WebSocket channel for real-time chat updates."""
        # This is just for testing WebSocket channel discovery
        # Chat service doesn't actually use @expose_ws in production
        return {'status': 'success', 'message': 'WebSocket channel working'}
    
    pass
