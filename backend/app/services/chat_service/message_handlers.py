from typing import Any, Dict

from .message_type_registry import MessageTypeHandler
from ...models.chat_message import ChatMessage
from ..tool_runtime import execute_tool
from ... import db
from datetime import datetime

class ChatMessageHandler(MessageTypeHandler):
    """Handle chat messages - explicit text messages."""

    def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        # ✅ ALL VALUES ARE MANDATORY AND DIRECT - NO SESSION LOOKUPS!

        message_text = content.get('text', '')
        if not message_text:
            return self._format_error_response('Text content is required for chat messages', 400)

        # Create chat message
        chat_msg = ChatMessage(
            history_id=history_id,          # ✅ Direct value
            role='user',
            message_type='chat',
            content_json=content,
            status='complete'
        )
        db.session.add(chat_msg)
        db.session.commit()

        # Emit WebSocket events
        session_id = session.id             # ✅ Direct from session
        chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': chat_msg.id,
            'role': chat_msg.role,
            'content': chat_msg.content_json,
            'timestamp': chat_msg.created_at.isoformat()
        })

        # Start AI processing - persona is DIRECT PARAMETER!
        asst_msg = chat_service._create_assistant_placeholder(history_id)
        chat_service._submit_message_for_async_processing(
            chat_msg.id, asst_msg.id, session_id, history_id, persona.id  # ✅ DIRECT persona.id!
        )

        return {
            'chat_message_id': chat_msg.id,
            'assistant_message_id': asst_msg.id,
            'status': 'processing',
            'websocket_channel': f'chat/{session_id}/{history_id}'
        }

class ToolCallMessageHandler(MessageTypeHandler):
    """Handle tool call messages - direct tool execution."""

    def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        # ✅ ALL VALUES ARE MANDATORY AND DIRECT - NO SESSION LOOKUPS!

        tool_name = content.get('tool')
        tool_args = content.get('args', {})

        # Create tool call message
        tool_call_msg = ChatMessage(
            history_id=history_id,          # ✅ Direct value
            role='user',
            message_type='tool_call',
            content_json=content,
            status='complete'
        )
        db.session.add(tool_call_msg)
        db.session.commit()

        # Emit WebSocket event for tool call received
        session_id = session.id             # ✅ Direct from session
        chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': tool_call_msg.id,
            'role': tool_call_msg.role,
            'message_type': 'tool_call',
            'content': tool_call_msg.content_json,
            'timestamp': tool_call_msg.created_at.isoformat()
        })

        # Emit WebSocket event for tool execution started
        chat_service.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)

        # Execute tool - persona is DIRECT PARAMETER!
        exec_result = execute_tool(persona.id, tool_name, tool_args)  # ✅ DIRECT persona.id!

        # Emit WebSocket event for tool execution completed
        chat_service.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)

        # Create tool result message
        tool_result_msg = ChatMessage(
            history_id=history_id,          # ✅ Direct value
            role='tool',
            message_type='tool',
            content_json={
                'toolName': tool_name,
                'toolParams': tool_args,
                'executionStatus': 'success' if exec_result.get('status') == 'success' else 'error',
                'result': exec_result,
                'executedBy': 'user',
                'executionTime': datetime.utcnow().isoformat()
            }
        )
        db.session.add(tool_result_msg)
        db.session.commit()

        # Emit WebSocket event for tool result message
        chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': tool_result_msg.id,
            'role': tool_result_msg.role,
            'message_type': 'tool',
            'content': tool_result_msg.content_json,
            'timestamp': tool_result_msg.created_at.isoformat()
        })

        return {
            'tool_call_message_id': tool_call_msg.id,
            'tool_result_message_id': tool_result_msg.id,
            'status': 'completed',
            'result': exec_result
        }
