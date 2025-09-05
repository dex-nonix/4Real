import uuid
from datetime import datetime, timezone
from typing import Any, Dict, TYPE_CHECKING

from nonix_web.utils.di import Inject
from nonix_web_db import AsyncSessionLocal
from .message_type_registry import MessageTypeHandler
from ...llm.agentic_tool_manager import AgenticToolManager
from ...models.chat_message import ChatMessage
from ...sequence_utils import next_seq

if TYPE_CHECKING:
    from ...routers.chat.chat_router import ChatRouter


class ChatMessageHandler(MessageTypeHandler):
    """Handle chat messages - explicit text messages."""

    async def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        message_text = content.get('text', '')
        if not message_text:
            raise ValueError('Text content is required for chat messages')

        # Create async database session
        async with AsyncSessionLocal() as db_session:
            # Create chat message
            turn = str(uuid.uuid4())
            seq_val = await next_seq(history_id)
            chat_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='user',
                content_json=content,
                status='complete',
                seq=seq_val,
                turn_id=turn
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
            'message_type': 'user',
            'content_json': chat_msg.content_json,
            'status': chat_msg.status,
            'seq': chat_msg.seq,
            'turn_id': chat_msg.turn_id,
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
    agentic_tool_manager: AgenticToolManager = Inject(AgenticToolManager)

    async def handle(self, chat_service: "ChatRouter", session, persona, history_id: int, content: Dict[str, Any]) -> \
            Dict[str, Any]:
        chat_service._logger.info(f"🔧 ToolCallMessageHandler received content: {content}")
        tool_name = content.get('tool')
        tool_args = content.get('args', {})
        chat_service._logger.info(f"🔧 Extracted tool_name: {tool_name}, tool_args: {tool_args}")

        # Create async database session
        async with AsyncSessionLocal() as db_session:
            # Create tool call message
            turn = str(uuid.uuid4())
            seq_val = await next_seq(history_id)
            tool_run = str(uuid.uuid4())
            tool_call_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='tool_call',
                content_json=content,
                status='complete',
                seq=seq_val,
                turn_id=turn,
                tool_run_id=tool_run
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
            'status': 'complete',  # Tool call message status
            'tool_name': tool_name,
            'tool_args': tool_args,
            'execution_status': None,  # Not applicable for tool_call
            'result': None,  # Not applicable for tool_call
            'executed_by': tool_call_msg.content_json.get('executed_by'),
            'execution_time': tool_call_msg.content_json.get('execution_time'),
            'execution_path': tool_call_msg.content_json.get('execution_path'),
            'seq': tool_call_msg.seq,
            'turn_id': tool_call_msg.turn_id,
            'tool_run_id': tool_call_msg.tool_run_id,
            'timestamp': tool_call_msg.created_at.isoformat()
        })

        # Emit WebSocket event for tool execution started
        await chat_service.emit_tool_event(
            session_id,
            history_id,
            tool_name,
            'started',
            args=tool_args,
            seq=tool_call_msg.seq,
            turn_id=tool_call_msg.turn_id,
            tool_run_id=tool_call_msg.tool_run_id
        )

        exec_result = await self.agentic_tool_manager.execute_tool(persona.id, tool_name, tool_args)

        # Create second async database session for tool result message
        async with AsyncSessionLocal() as db_session:
            # Create tool result message
            seq_val_res = await next_seq(history_id)
            tool_result_msg = ChatMessage(
                history_id=history_id,
                role='tool',
                message_type='tool_result',
                status='complete',  # ✅ FIXED: Add required status field
                content_json={
                    'tool_name': tool_name,  # ✅ Standardized: snake_case
                    'tool_args': tool_args,  # ✅ Standardized: snake_case
                    'execution_status': 'success' if exec_result.get('status') == 'success' else 'error',
                    # ✅ Standardized: snake_case
                    'result': exec_result,  # ✅ Consistent field
                    'executed_by': 'user',  # ✅ Standardized: snake_case
                    'execution_time': datetime.now(timezone.utc).isoformat(),  # ✅ Standardized: snake_case
                    'execution_path': 'manual'  # ✅ Standardized: execution path identifier
                },
                seq=seq_val_res,
                turn_id=tool_call_msg.turn_id,
                tool_run_id=tool_call_msg.tool_run_id
            )

            # Use async database operations
            db_session.add(tool_result_msg)
            await db_session.commit()
            await db_session.refresh(tool_result_msg)

        # Emit WebSocket event for tool result message
        await chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': tool_result_msg.id,
            'role': tool_result_msg.role,
            'message_type': 'tool_result',
            'tool_name': tool_result_msg.content_json.get('tool_name'),
            'tool_args': tool_result_msg.content_json.get('tool_args'),
            'execution_status': tool_result_msg.content_json.get('execution_status'),
            'result': tool_result_msg.content_json.get('result'),
            'executed_by': tool_result_msg.content_json.get('executed_by'),
            'execution_time': tool_result_msg.content_json.get('execution_time'),
            'execution_path': tool_result_msg.content_json.get('execution_path'),
            'status': tool_result_msg.status if hasattr(tool_result_msg, 'status') else 'complete',
            'seq': tool_result_msg.seq,
            'turn_id': tool_result_msg.turn_id,
            'tool_run_id': tool_result_msg.tool_run_id,
            'timestamp': tool_result_msg.created_at.isoformat()
        })

        # Emit WebSocket event for tool execution completed (after result message is persisted)
        await chat_service.emit_tool_event(
            session_id,
            history_id,
            tool_name,
            'completed',
            result=exec_result,
            seq=tool_result_msg.seq,
            turn_id=tool_result_msg.turn_id,
            tool_run_id=tool_result_msg.tool_run_id
        )

        return {
            'tool_call_message_id': tool_call_msg.id,
            'tool_result_message_id': tool_result_msg.id,
            'status': 'completed',
            'result': exec_result
        }
