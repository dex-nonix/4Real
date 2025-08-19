from __future__ import annotations

from flask import jsonify, Request

from ...decorators import expose
from ... import db
from ...models.chat_session import ChatSession
from ...models.chat_message import ChatMessage
from ...models.chat_history import ChatHistory
from ...models.persona import Persona
from ..llm_client import run_chat
from ..tool_runtime import build_persona_tool_map, execute_tool, list_persona_tools
from ..base_api_service import BaseApiService
from datetime import datetime

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
    
    def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict) -> None:
        """IMPLEMENT: Emit chat event using BaseApiService method."""
        channel = f'chat/{session_id}/{history_id}'
        print(f"🔌 ChatService.emit_chat_event: channel={channel}, event={event}, data={data}")
        self.send_to_channel(channel, event, data)
    
    def emit_llm_event(self, session_id: int, history_id: int, stage: str, message: str) -> None:
        """IMPLEMENT: Emit LLM status event."""
        self.emit_chat_event(session_id, history_id, 'llm_status', {
            'stage': stage,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra) -> None:
        """IMPLEMENT: Emit tool execution event."""
        self.emit_chat_event(session_id, history_id, 'tool_status', {
            'tool_name': tool_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            **extra
        }) 