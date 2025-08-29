from __future__ import annotations

from typing import Any, Dict, List

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from nonix_web.services.base_service import route
from nonix_web_db import AsyncSessionLocal
from .models_and_schemas import (
    MessageListResponse,
    SendMessageToHistoryRequest,
    DeleteMessageResponse,
    MessageResponse
)
from ..message_handlers import ChatMessageHandler, ToolCallMessageHandler
from ..message_type_registry import message_type_registry
from ..streaming_event_manager import StreamingEventManager
from ..streaming_interface import StreamingChunk
from ..streaming_message_handler import StreamingMessageHandler
from ..websocket_protocol import WebSocketMixinProtocol
from ....models.ai_model_mapping import AIModelMapping
from ....models.ai_provider import AIProvider
from ....models.chat_history import ChatHistory
from ....models.chat_message import ChatMessage
from ....models.chat_session import ChatSession
from ....models.persona import Persona
from ....models.tool_invocation_log import ToolInvocationLog


class ChatMessageMixin(WebSocketMixinProtocol):
    """Mixin for chat message handling and sending operations."""

    def __init__(self):
        """Initialize message type handlers."""
        # Register message type handlers
        message_type_registry.register('chat', ChatMessageHandler())
        message_type_registry.register('tool_call', ToolCallMessageHandler())

    async def _select_chat_model(self, persona_id: int) -> Dict[str, Any] | None:
        """Select AI model for persona with strict validation."""
        self._logger.debug(f"Selecting AI model for persona {persona_id}")

        async with AsyncSessionLocal() as db_session:
            persona = (await db_session.execute(
                select(Persona).where(Persona.id == persona_id)
            )).scalar_one_or_none()

            if not persona:
                self._logger.warning(f"Persona {persona_id} not found")
                return None

            mapping = None
            if persona and getattr(persona, 'ai_model_mapping_id', None):
                mapping = (await db_session.execute(
                    select(AIModelMapping).where(AIModelMapping.id == persona.ai_model_mapping_id,
                                                 AIModelMapping.is_active == True)
                )).scalar_one_or_none()
                self._logger.debug(f"AI model mapping found: {mapping}")
            else:
                self._logger.warning(f"Persona {persona_id} has no AI model mapping")

            if not mapping:
                self._logger.warning(f"No active AI model mapping found for persona {persona_id}")
                return None

            model_info = {
                'provider_id': mapping.provider_id,
                'model_name': mapping.model_name,
                'parameters': mapping.parameters_json or {},
            }
            self._logger.info(f"Selected AI model: {mapping.model_name} (provider: {mapping.provider_id})")
            return model_info

    async def _validate_session_history(self, session_id: int, history_id: int = None):
        """Validate session and history, return tuple (session, history)."""
        self._logger.debug(f"Validating session {session_id} with history {history_id}")

        async with AsyncSessionLocal() as db_session:
            # Load session with persona relationship eagerly
            session_result = await db_session.execute(
                select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
            )
            session = session_result.scalar_one_or_none()

            if not session:
                self._logger.warning(f"Session {session_id} not found or inactive")
                return None, None

            # Load persona relationship eagerly to avoid detached instance errors
            await db_session.refresh(session, ['persona'])

            if history_id:
                # Specific history requested
                self._logger.debug(f"Querying history {history_id} for session {session_id}")

                history_result = await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )
                history = history_result.scalar_one_or_none()
                self._logger.debug(f"History query result: {history}")

                if not history:
                    self._logger.warning(f"History {history_id} not found for session {session_id}")
                    return session, None
            else:
                # Use current history or create new one
                if not session.current_history_id:
                    self._logger.info(f"Creating new history for session {session_id}")
                    history = ChatHistory(
                        session_id=session_id,
                        title='New Conversation',
                        message_count=0
                    )
                    db_session.add(history)
                    await db_session.commit()
                    await db_session.refresh(history)
                    session.current_history_id = history.id
                    await db_session.commit()
                    self._logger.info(f"New history {history.id} created for session {session_id}")
                else:
                    self._logger.debug(f"Using existing history {session.current_history_id} for session {session_id}")
                    history = await db_session.get(ChatHistory, session.current_history_id)
                    if not history:
                        self._logger.warning(
                            f"Current history {session.current_history_id} not found for session {session_id}")
                        return session, None

            self._logger.debug(
                f"Session validation successful: session={session.id}, history={history.id if history else None}")
            return session, history

    async def _create_user_message(self, history_id: int, content: Dict[str, Any]) -> ChatMessage:
        """Create and save user message."""
        self._logger.debug(f"Creating user message for history {history_id}")

        async with AsyncSessionLocal() as db_session:
            user_msg = ChatMessage(
                history_id=history_id,
                role='user',
                message_type='text',
                content_json=content
            )
            db_session.add(user_msg)
            await db_session.commit()
            await db_session.refresh(user_msg)

            self._logger.info(f"User message {user_msg.id} created successfully for history {history_id}")
            return user_msg

    async def create_assistant_placeholder(self, history_id: int) -> ChatMessage:
        """Create empty assistant message placeholder."""
        self._logger.debug(f"Creating assistant message placeholder for history {history_id}")

        async with AsyncSessionLocal() as db_session:
            asst_msg = ChatMessage(
                history_id=history_id,
                role='assistant',
                message_type='text',
                content_json={'type': 'text', 'text': ''},
                status='processing'
            )
            db_session.add(asst_msg)
            await db_session.commit()
            await db_session.refresh(asst_msg)

            self._logger.info(f"Assistant message placeholder {asst_msg.id} created for history {history_id}")
            return asst_msg

    async def _build_chat_history(self, history_id: int, user_msg_id: int) -> List[Dict[str, Any]]:
        """Build chat history for LLM processing."""
        self._logger.debug(f"Building chat history for history {history_id} up to message {user_msg_id}")

        async with AsyncSessionLocal() as db_session:
            chat_history = []

            # Add system messages
            system_result = await db_session.execute(
                select(ChatMessage).where(ChatMessage.history_id == history_id, ChatMessage.role == 'system').order_by(
                    ChatMessage.created_at.asc())
            )
            system_msgs = system_result.scalars().all()
            self._logger.debug(f"Found {len(system_msgs)} system messages")
            for sm in system_msgs:
                content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
                chat_history.append({'role': 'system', 'content': content})

            # Add user and assistant messages up to current user message
            user_result = await db_session.execute(
                select(ChatMessage).where(ChatMessage.history_id == history_id,
                                          ChatMessage.id <= user_msg_id).order_by(
                    ChatMessage.created_at.asc())
            )
            user_msgs = user_result.scalars().all()
            self._logger.debug(f"Found {len(user_msgs)} user/assistant messages")
            for um in user_msgs:
                role = um.role
                if role not in ('user', 'assistant'):
                    continue
                content = um.content_json if isinstance(um.content_json, dict) else {'text': str(um.content_json)}
                chat_history.append({'role': role, 'content': content})

            self._logger.info(f"Built chat history with {len(chat_history)} total messages")
            return chat_history

    async def _resolve_ai_model(self, persona_id: int):
        """Resolve AI model, provider, and mapping."""
        self._logger.debug(f"Resolving AI model components for persona {persona_id}")

        model_info = await self._select_chat_model(persona_id)
        if not model_info:
            self._logger.warning(f"Failed to select AI model for persona {persona_id}")
            return None, None, None

        async with AsyncSessionLocal() as db_session:
            provider = (await db_session.execute(
                select(AIProvider).where(AIProvider.id == model_info['provider_id'], AIProvider.is_active == True)
            )).scalar_one_or_none()

            if not provider:
                self._logger.warning(f"AI provider {model_info['provider_id']} not found or inactive")
                return None, None, None

            # FIX: use persona.ai_model_mapping_id rather than persona_id
            mapping_obj = (await db_session.execute(
                select(AIModelMapping).where(AIModelMapping.id == (await db_session.execute(
                    select(Persona.ai_model_mapping_id).where(Persona.id == persona_id)
                )).scalar_one_or_none(), AIModelMapping.is_active == True)
            )).scalar_one_or_none()

            if not mapping_obj:
                self._logger.warning(f"AI model mapping not found or inactive for persona {persona_id}")
                return None, None, None

            self._logger.info(
                f"AI model resolved successfully: provider={provider.name}, model={model_info['model_name']}")
            return model_info, provider, mapping_obj

    async def _execute_tool_call(self, persona_id: int, tool_name: str, tool_args: Dict[str, Any],
                                 history_id: int, user_msg_id: int, available_tools: Dict[str, Any]):
        """Execute tool call and return result."""
        self._logger.info(f"Executing tool '{tool_name}' for persona {persona_id}")
        self._logger.debug(f"Tool arguments: {tool_args}")

        if tool_name not in available_tools:
            self._logger.warning(f"Tool '{tool_name}' not allowed for persona {persona_id}")
            return None, f'Tool {tool_name} not allowed'

        async with AsyncSessionLocal() as db_session:
            # Log tool execution
            log = ToolInvocationLog(
                history_id=history_id,
                message_id=user_msg_id,
                tool_name=tool_name,
                input_json=tool_args,
                status='started'
            )
            db_session.add(log)
            await db_session.commit()
            await db_session.refresh(log)
            self._logger.debug(f"Tool invocation logged with ID {log.id}")

            # Execute tool
            self._logger.debug(f"Calling execute_tool for '{tool_name}'")
            exec_result = await self.agentic_tool_manager.execute_tool(persona_id, tool_name, tool_args)
            log.status = 'success' if exec_result.get('status') == 'success' else 'error'
            log.output_json = exec_result
            await db_session.commit()

            status = 'success' if exec_result.get('status') == 'success' else 'error'
            self._logger.info(f"Tool '{tool_name}' execution completed with status: {status}")

            # Create tool result message
            tool_msg = ChatMessage(
                history_id=history_id,
                role='tool',
                message_type='tool_result',
                content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result}
            )
            db_session.add(tool_msg)
            await db_session.commit()
            await db_session.refresh(tool_msg)
            self._logger.debug(f"Tool result message {tool_msg.id} created")

            return exec_result, None

    async def _create_assistant_message(self, history_id: int, content: Dict[str, Any],
                                        status: str = 'complete') -> ChatMessage:
        """Create and save assistant message."""
        self._logger.debug(f"Creating assistant message for history {history_id} with status '{status}'")

        async with AsyncSessionLocal() as db_session:
            asst_msg = ChatMessage(
                history_id=history_id,
                role='assistant',
                message_type='text',
                content_json=content,
                status=status
            )
            db_session.add(asst_msg)
            await db_session.commit()
            await db_session.refresh(asst_msg)

            self._logger.info(f"Assistant message {asst_msg.id} created successfully for history {history_id}")
            return asst_msg

    async def _format_error_response(self, error_message: str, status_code: int = 400):
        """Format error response consistently."""
        return JSONResponse({'error': error_message}, status_code)

    @route(
        '/sessions/{id}/messages',
        methods=['GET'],
        response_model=MessageListResponse
    )
    async def list_messages(self, req: Request, id: int):  # noqa: A002
        """List messages from a chat session's current history."""
        try:
            async with AsyncSessionLocal() as db_session:
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

                # Get messages from current history
                if not session.current_history_id:
                    return {'data': [], 'total': 0}

                msgs = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == session.current_history_id).order_by(
                        ChatMessage.created_at.asc())
                ).scalars().all()

                return {'data': [m.to_dict() for m in msgs], 'total': len(msgs)}
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, status_code=500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/send',
        methods=['POST'],
        response_model=MessageResponse
    )
    async def send_message(
            self,
            req: Request,
            payload: SendMessageToHistoryRequest,
            session_id: int = None,
            history_id: int = None
    ):
        """Send message to session."""
        self._logger.info(f"Processing send_message request for session {session_id}, history {history_id}")

        try:
            session_id = int(session_id)
            if history_id:
                history_id = int(history_id)

            self._logger.debug(f"Parameter conversion: session_id={session_id}, history_id={history_id}")

            session, history = await self._validate_session_history(session_id, history_id)
            if not session:
                self._logger.warning(f"Session {session_id} not found")
                return await self._format_error_response('Session not found', 404)

            persona = session.persona
            if not persona:
                self._logger.warning(f"Session {session_id} has no persona")
                return await self._format_error_response('Session has no persona', 400)
            if not persona.is_active:
                self._logger.warning(f"Persona {persona.id} is not active")
                return await self._format_error_response('Persona is not active', 400)

            if not history_id:
                self._logger.debug(
                    f"No history_id provided, using session.current_history_id: {session.current_history_id}")
                history_id = session.current_history_id
                if not history_id:
                    self._logger.warning(f"No current history found for session {session_id}")
                    return await self._format_error_response('No current history', 400)
            else:
                self._logger.debug(f"History_id provided: {history_id}, history object: {history}")
                # Validate provided history_id belongs to session
                if not history or history.session_id != session_id:
                    self._logger.warning(f"History validation failed - history: {history}, session_id: {session_id}")
                    return await self._format_error_response('History not found or invalid', 404)

            # Get user content - MUST be object with type
            user_content = payload.content
            if not user_content:
                return await self._format_error_response('content required', 400)

            if not isinstance(user_content, dict) or 'type' not in user_content:
                return await self._format_error_response('Content must be object with explicit type', 400)

            # Get message type
            message_type = user_content.get('type')
            if not message_type:
                return await self._format_error_response('Message type is required', 400)

            self._logger.info(f"Processing message type: {message_type}")
            self._logger.debug(f"Available message types: {message_type_registry.list_types()}")
            self._logger.debug(
                f"Handler found for type '{message_type}': {message_type_registry.has_handler(message_type)}")

            # Get handler from registry
            handler = message_type_registry.get_handler(message_type)
            self._logger.debug(f"Message handler resolved: {type(handler).__name__}")
            if not handler:
                self._logger.error(f"Unknown message type: {message_type}")
                return await self._format_error_response(f'Unknown message type: {message_type}', 400)

            result = await handler.handle(
                chat_service=self,
                session=session,
                persona=persona,
                history_id=history_id,  # ALWAYS provided (extracted or from URL)
                content=user_content
            )

            self._logger.info(f"Message processed successfully by handler, returning result")
            return JSONResponse({'data': result})

        except Exception as exc:
            self._logger.error(f"Error in send_message: {exc}", exc_info=True)
            return await self._format_error_response(str(exc), 500)

    async def submit_message_for_async_processing(
            self,
            user_msg_id: int,
            asst_msg_id: int,
            session_id: int,
            history_id: int,
            persona_id: int
    ):
        """Submit message processing to task manager for async execution."""
        try:
            # Use the task manager from the parent ChatService
            future = await self.submit_async_task(
                self._process_message_async,
                user_msg_id,
                asst_msg_id,
                session_id,
                history_id,
                persona_id
            )

            # Log successful submission with proper logger
            self._logger.info(f"Message {user_msg_id} submitted to task manager for async processing")
            return future

        except Exception as e:
            # Log error with full stack trace
            self._logger.error(f"Failed to submit message {user_msg_id} to task manager: {e}", exc_info=True)
            # Emit error event
            await self.emit_llm_event(session_id, history_id, 'processing_failed', f'Failed to start processing: {e}')
            raise

    async def _process_message_async(
            self,
            user_msg_id: int,
            asst_msg_id: int,
            session_id: int,
            history_id: int,
            persona_id: int
    ):
        """Process message asynchronously using streaming."""
        message_handler = StreamingMessageHandler(session_id, history_id)
        event_manager = StreamingEventManager(self)
        accumulated_text = ""
        try:
            # Set the existing assistant message ID
            message_handler.assistant_message_id = asst_msg_id

            # Validate message exists
            if not await message_handler.ensure_message_exists():
                error_msg = "Assistant message not found or inaccessible"
                await self.emit_llm_event(session_id, history_id, 'processing_failed', error_msg)
                return

            # Get model info and tools
            model_info, provider, mapping_obj = await self._resolve_ai_model(persona_id)
            available_tools_info = await self.agentic_tool_manager.list_persona_tools(persona_id)
            if not model_info or not provider or not mapping_obj:
                # No model available - mark as failed
                error_msg = "AI model, provider, or mapping not available"
                await message_handler.mark_as_error(error_msg)
                await event_manager.emit_chunk_event(
                    session_id,
                    history_id,
                    StreamingChunk(content="", chunk_type="complete", is_final=True),
                    asst_msg_id
                )
                return

            # Build chat history using helper method
            chat_history = await self._build_chat_history(history_id, user_msg_id)

            # Use streaming LLM client
            try:
                async for message in self.run_chat_streaming(
                        provider,
                        mapping_obj,
                        chat_history,
                        available_tools_info,
                        persona_id
                ):
                    # message is already a StreamingChunk

                    # Handle each chunk
                    if message.chunk_type == "text":
                        # accumulate full text for final persistence
                        accumulated_text += message.content or ""
                        if await message_handler.update_content_safely(message.content):
                            await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)
                        else:
                            # Log error but continue processing
                            self._logger.error(f"Failed to update content for chunk: {message.content[:50]}...")

                    elif message.chunk_type == "ai_start":
                        await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)

                    elif message.chunk_type == "tool_start":
                        await event_manager.emit_tool_event(session_id, history_id,
                                                            message.metadata.get("tool_name", ""), "started")

                    elif message.chunk_type == "tool_end":
                        await event_manager.emit_tool_event(session_id, history_id,
                                                            message.metadata.get("tool_name", ""), "completed")

                    elif message.chunk_type == "complete":
                        await message_handler.finalize_assistant_message(accumulated_text if accumulated_text else None)
                        await event_manager.emit_chunk_event(session_id, history_id, message, asst_msg_id)
                        break

            except Exception as e:
                # Handle streaming errors
                await message_handler.mark_as_error(f"Streaming error: {str(e)}")
                await message_handler.cleanup_on_error()  # Clean up on error
                await event_manager.emit_streaming_error(
                    session_id,
                    history_id,
                    f"Streaming error: {str(e)}",
                    "streaming_error",
                    asst_msg_id
                )
                await self.emit_llm_event(session_id, history_id, 'processing_failed', f"Streaming error: {str(e)}")

        except Exception as e:
            await message_handler.cleanup_on_error()
            await self.emit_llm_event(
                session_id,
                history_id,
                'processing_failed',
                f"Async processing error: {str(e)}"
            )
            self._logger.error(f"Error in _process_message_async: {e}", exc_info=True)

    # @expose(
    #     '/sessions/{session_id}/retry',
    #     methods=['POST'],
    #     status_codes={200: 'OK', 400: 'Bad Request'},
    #     response_schema={
    #         "type": "object",
    #         "properties": {
    #             "data": {
    #                 "type": "object",
    #                 "properties": {
    #                     "id": {"type": "integer"},
    #                     "history_id": {"type": "integer"},
    #                     "role": {"type": "string"},
    #                     "message_type": {"type": "string"},
    #                     "content_json": {"type": "object"},
    #                     "created_at": {"type": "string", "format": "date-time"},
    #                     "updated_at": {"type": "string", "format": "date-time"}
    #                 }
    #             }
    #         }
    #     }
    # )
    # @expose(
    #     '/sessions/{session_id}/histories/{history_id}/retry',
    #     methods=['POST'],
    #     status_codes={200: 'OK', 400: 'Bad Request'},
    #     response_schema={
    #         "type": "object",
    #         "properties": {
    #             "data": {
    #                 "type": "object",
    #                 "properties": {
    #                     "id": {"type": "integer"},
    #                     "history_id": {"type": "integer"},
    #                     "role": {"type": "string"},
    #                     "message_type": {"type": "string"},
    #                     "content_json": {"type": "object"},
    #                     "created_at": {"type": "string", "format": "date-time"},
    #                     "updated_at": {"type": "string", "format": "date-time"}
    #                 }
    #             }
    #         }
    #     }
    # )
    # def retry_last(self, req: Request, session_id: int, history_id: int = None):
    #     """Retry the last user message in a session - history_id is OPTIONAL in URL."""
    #     try:
    #         session, history = self._validate_session_history(session_id, history_id)
    #         if not session:
    #             return await self._format_error_response('Session not found', 404)
    #
    #         # OPTIONAL EXTRACTION: If no history_id provided, extract from session
    #         if not history_id:
    #             history_id = session.current_history_id
    #             if not history_id:
    #                 return await self._format_error_response('No current history', 400)
    #         else:
    #             # Validate provided history_id belongs to session
    #             if not history or history.session_id != session_id:
    #                 return await self._format_error_response('History not found or invalid', 404)
    #
    #         last_user = ChatMessage.query.filter_by(session_id=session_id, role='user').order_by(
    #             ChatMessage.created_at.desc()).first()
    #         if not last_user:
    #             return await self._format_error_response('No user messages', 400)
    #         # Reuse send logic by re-sending the last user content
    #         mock_req = type('obj', (), {'get_json': lambda self, silent=True: {'content': last_user.content_json}})()
    #         return self.send_message(mock_req, session_id, history_id)
    #     except Exception as exc:  # noqa: BLE001
    #         return await self._format_error_response(str(exc), 500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages',
        methods=['GET'],
        response_model=MessageListResponse
    )
    async def list_history_messages(self, req: Request, session_id: int, history_id: int):
        """Get messages from a specific history within a session."""
        try:
            # Validate session and history
            session, history = await self._validate_session_history(session_id, history_id)
            if not session:
                return await self._format_error_response('Session not found or inactive', 404)
            if not history:
                return await self._format_error_response('History not found', 404)

            async with AsyncSessionLocal() as db_session:
                result = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == history_id).order_by(
                        ChatMessage.created_at.asc())
                )
                msgs = result.scalars().all()
                return JSONResponse({'data': [m.to_dict() for m in msgs], 'total': len(msgs)})
        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages',
        methods=['DELETE'],
        response_model=DeleteMessageResponse
    )
    async def clear_history_messages(self, req: Request, session_id: int, history_id: int):
        """Clear all messages from a specific history."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Verify session exists and is active
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    return await self._format_error_response('Session not found or inactive', 404)

                # Verify history exists and belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    return await self._format_error_response('History not found', 404)

                # Count messages before deletion
                messages_result = await db_session.execute(
                    select(ChatMessage).where(ChatMessage.history_id == history_id)
                )
                messages = messages_result.scalars().all()
                deleted_count = len(messages)

                # Delete all messages in the history
                for message in messages:
                    await db_session.delete(message)

                # Reset history message count
                history.message_count = 0

                await db_session.commit()

                return JSONResponse({
                    'message': f'Successfully cleared {deleted_count} messages from history',
                    'deleted_count': deleted_count
                })

        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)

    @route(
        '/sessions/{session_id}/histories/{history_id}/messages/{message_id}',
        methods=['DELETE'],
        response_model=DeleteMessageResponse
    )
    async def delete_message(self, req: Request, session_id: int, history_id: int, message_id: int):
        """Delete a specific message from a history."""
        try:
            async with AsyncSessionLocal() as db_session:
                # Verify session exists and is active
                session = (await db_session.execute(
                    select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
                )).scalar_one_or_none()

                if not session:
                    return await self._format_error_response('Session not found or inactive', 404)

                # Verify history exists and belongs to session
                history = (await db_session.execute(
                    select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
                )).scalar_one_or_none()

                if not history:
                    return await self._format_error_response('History not found', 404)

                # Find and delete the specific message
                message = (await db_session.execute(
                    select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.history_id == history_id)
                )).scalar_one_or_none()

                if not message:
                    return await self._format_error_response('Message not found', 404)

                # Store message ID before deletion for response
                deleted_message_id = message.id

                # Delete the message
                await db_session.delete(message)

                # Update history message count
                history.message_count = max(0, history.message_count - 1)

                await db_session.commit()

                return JSONResponse({
                    'message': 'Message deleted successfully',
                    'deleted_message_id': deleted_message_id
                })

        except Exception as exc:  # noqa: BLE001
            return await self._format_error_response(str(exc), 500)
