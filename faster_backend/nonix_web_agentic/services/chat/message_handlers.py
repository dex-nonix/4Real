from datetime import datetime, timezone
from typing import Any, Dict, TYPE_CHECKING

from nonix_web.utils.di import Inject
from nonix_web_db import AsyncSessionLocal
from .message_type_registry import MessageTypeHandler
from ...llm.agentic_tool_manager import AgenticToolManager
from ...models.chat_message import ChatMessage

if TYPE_CHECKING:
    from .chat_service import ChatService


class ChatMessageHandler(MessageTypeHandler):
    """Handle chat messages - explicit text messages."""

    async def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        message_text = content.get('text', '')
        if not message_text:
            raise ValueError('Text content is required for chat messages')

        # Create async database session
        async with AsyncSessionLocal() as db_session:
            # Create chat message
            chat_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='text',
                content_json=content,
                status='complete'
            )

            # Use async database operations
            db_session.add(chat_msg)
            await db_session.commit()
            await db_session.refresh(chat_msg)

        # Emit WebSocket events
        session_id = session.id
        await chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': chat_msg.id,
            'role': chat_msg.role,
            'content': chat_msg.content_json,
            'timestamp': chat_msg.created_at.isoformat()
        })

        # Start AI processing - persona is DIRECT PARAMETER!
        asst_msg = await chat_service.create_assistant_placeholder(history_id)
        await chat_service.submit_message_for_async_processing(
            chat_msg.id,
            asst_msg.id,
            session_id,
            history_id,
            persona.id
        )

        return {
            'chat_message_id': chat_msg.id,
            'assistant_message_id': asst_msg.id,
            'status': 'processing',
            'websocket_room': f'chat/{session_id}/{history_id}'
        }


class ToolCallMessageHandler(MessageTypeHandler):
    """Handle tool call messages - direct tool execution."""
    agentic_tool_manager:AgenticToolManager = Inject(AgenticToolManager)

    async def handle(self, chat_service: "ChatService", session, persona, history_id: int, content: Dict[str, Any]) -> \
    Dict[str, Any]:
        tool_name = content.get('tool')
        tool_args = content.get('args', {})

        # Create async database session
        async with AsyncSessionLocal() as db_session:
            # Create tool call message
            tool_call_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='tool_call',
                content_json=content,
                status='complete'
            )

            # Use async database operations
            db_session.add(tool_call_msg)
            await db_session.commit()
            await db_session.refresh(tool_call_msg)

        # Emit WebSocket event for tool call received
        session_id = session.id
        await chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': tool_call_msg.id,
            'role': tool_call_msg.role,
            'message_type': 'tool_call',
            'content': tool_call_msg.content_json,
            'timestamp': tool_call_msg.created_at.isoformat()
        })

        # Emit WebSocket event for tool execution started
        await chat_service.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)

        exec_result = await self.agentic_tool_manager.execute_tool(persona.id, tool_name, tool_args)

        # Emit WebSocket event for tool execution completed
        await chat_service.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)

        # Create second async database session for tool result message
        async with AsyncSessionLocal() as db_session:
            # Create tool result message
            tool_result_msg = ChatMessage(
                history_id=history_id,
                role='tool',
                message_type='tool',
                content_json={
                    'toolName': tool_name,
                    'toolParams': tool_args,
                    'executionStatus': 'success' if exec_result.get('status') == 'success' else 'error',
                    'result': exec_result,
                    'executedBy': 'user',
                    'executionTime': datetime.now(timezone.utc).isoformat()
                }
            )

            # Use async database operations
            db_session.add(tool_result_msg)
            await db_session.commit()
            await db_session.refresh(tool_result_msg)

        # Emit WebSocket event for tool result message
        await chat_service.emit_chat_event(session_id, history_id, 'message_received', {
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
