from __future__ import annotations

from typing import Any, Dict, List
from flask import jsonify, Request
from ...decorators import expose
from ... import db
from ...models.chat_session import ChatSession
from ...models.chat_message import ChatMessage
from ...models.chat_history import ChatHistory
from ...models.persona import Persona
from ...models.tool_invocation_log import ToolInvocationLog
from ...models.ai_model_mapping import AIModelMapping
from ...models.ai_provider import AIProvider
from ..tool_runtime import execute_tool
from .websocket_protocol import WebSocketProtocol
from ..tool_runtime import list_persona_tools
from .streaming_interface import StreamingChunk
from .streaming_message_handler import StreamingMessageHandler
from .streaming_event_manager import StreamingEventManager
from ..llm_client import run_chat_streaming


class ChatMessageMixin(WebSocketProtocol):
    """Mixin for chat message handling and sending operations."""

    def _select_chat_model(self, persona_id: int) -> Dict[str, Any] | None:
        # Strict persona selection: require persona.ai_model_mapping_id
        persona = Persona.query.filter_by(id=persona_id).first()
        mapping = None
        if persona and getattr(persona, 'ai_model_mapping_id', None):
            mapping = AIModelMapping.query.filter_by(id=persona.ai_model_mapping_id, is_active=True).first()
        if not mapping:
            return None
        return {
            'provider_id': mapping.provider_id,
            'model_name': mapping.model_name,
            'parameters': mapping.parameters_json or {},
        }

    def _validate_session_history(self, session_id: int, history_id: int = None):
        """Validate session and history, return tuple (session, history)."""
        session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
        if not session:
            return None, None
        
        if history_id:
            # Specific history requested
            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return session, None
        else:
            # Use current history or create new one
            if not session.current_history_id:
                history = ChatHistory(
                    session_id=session_id,
                    title='New Conversation',
                    message_count=0
                )
                db.session.add(history)
                db.session.commit()
                session.current_history_id = history.id
                db.session.commit()
            else:
                history = ChatHistory.query.get(session.current_history_id)
                if not history:
                    return session, None
        
        return session, history

    def _create_user_message(self, history_id: int, content: Dict[str, Any]) -> ChatMessage:
        """Create and save user message."""
        user_msg = ChatMessage(
            history_id=history_id,
            role='user',
            message_type='text',
            content_json=content
        )
        db.session.add(user_msg)
        db.session.commit()
        return user_msg

    def _create_assistant_placeholder(self, history_id: int) -> ChatMessage:
        """Create empty assistant message placeholder."""
        asst_msg = ChatMessage(
            history_id=history_id,
            role='assistant',
            message_type='text',
            content_json={'type': 'text', 'text': ''},
            status='processing'
        )
        db.session.add(asst_msg)
        db.session.commit()
        return asst_msg

    def _build_chat_history(self, history_id: int, user_msg_id: int) -> List[Dict[str, Any]]:
        """Build chat history for LLM processing."""
        chat_history = []
        
        # Add system messages
        system_msgs = ChatMessage.query.filter_by(history_id=history_id, role='system').order_by(ChatMessage.created_at.asc()).all()
        for sm in system_msgs:
            content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
            chat_history.append({'role': 'system', 'content': content})
        
        # Add user and assistant messages up to current user message
        user_msgs = ChatMessage.query.filter(ChatMessage.history_id==history_id, ChatMessage.id<=user_msg_id).order_by(ChatMessage.created_at.asc()).all()
        for um in user_msgs:
            role = um.role
            if role not in ('user', 'assistant'):
                continue
            content = um.content_json if isinstance(um.content_json, dict) else {'text': str(um.content_json)}
            chat_history.append({'role': role, 'content': content})
        
        return chat_history

    def _resolve_ai_model(self, persona_id: int):
        """Resolve AI model, provider, and mapping."""
        model_info = self._select_chat_model(persona_id)
        if not model_info:
            return None, None, None
        
        provider = AIProvider.query.filter_by(id=model_info['provider_id'], is_active=True).first()
        mapping_obj = AIModelMapping.query.filter_by(id=persona_id, is_active=True).first()
        
        return model_info, provider, mapping_obj

    def _execute_tool_call(self, persona_id: int, tool_name: str, tool_args: Dict[str, Any], 
                          history_id: int, user_msg_id: int, available_tools: Dict[str, Any]):
        """Execute tool call and return result."""
        if tool_name not in available_tools:
            return None, f'Tool {tool_name} not allowed'
        
        # Log tool execution
        log = ToolInvocationLog(
            history_id=history_id,
            message_id=user_msg_id,
            tool_name=tool_name,
            input_json=tool_args,
            status='started'
        )
        db.session.add(log)
        db.session.commit()

        # Execute tool
        exec_result = execute_tool(persona_id, tool_name, tool_args)
        log.status = 'success' if exec_result.get('status') == 'success' else 'error'
        log.output_json = exec_result
        db.session.commit()

        # Create tool result message
        tool_msg = ChatMessage(
            history_id=history_id,
            role='tool',
            message_type='tool_result',
            content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result}
        )
        db.session.add(tool_msg)
        db.session.commit()

        return exec_result, None

    def _create_assistant_message(self, history_id: int, content: Dict[str, Any], status: str = 'complete') -> ChatMessage:
        """Create and save assistant message."""
        asst_msg = ChatMessage(
            history_id=history_id,
            role='assistant',
            message_type='text',
            content_json=content,
            status=status
        )
        db.session.add(asst_msg)
        db.session.commit()
        return asst_msg

    def _format_error_response(self, error_message: str, status_code: int = 400):
        """Format error response consistently."""
        return jsonify({'error': error_message}), status_code

    @expose(
        '/sessions/{id}/messages', 
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "history_id": {"type": "integer"},
                            "role": {"type": "string"},
                            "message_type": {"type": "string"},
                            "content_json": {"type": "object"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
    def list_messages(self, req: Request, id: int):  # noqa: A002
        """List messages from a chat session's current history."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            # Get messages from current history
            if not session.current_history_id:
                return jsonify({'data': [], 'total': 0})

            msgs = ChatMessage.query.filter_by(history_id=session.current_history_id).order_by(ChatMessage.created_at.asc()).all()
            return jsonify({'data': [m.to_dict() for m in msgs], 'total': len(msgs)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose(
        '/sessions/{id}/send', 
        methods=['POST'],
        status_codes={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "object",
                    "description": "Message content in JSON format",
                    "additionalProperties": True
                }
            },
            "required": ["content"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "history_id": {"type": "integer"},
                        "role": {"type": "string"},
                        "message_type": {"type": "string"},
                        "content_json": {"type": "object"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    def send_message(self, req: Request, id: int):  # noqa: A002
        """Send a message to a chat session."""
        try:
            # Validate session and get/create history
            session, history = self._validate_session_history(id)
            if not session:
                return self._format_error_response('Session not found or inactive', 404)
            if not history:
                return self._format_error_response('Current history not found', 404)

            # Get user content
            payload = req.get_json(silent=True) or {}
            user_content = payload.get('content')
            if not user_content:
                return self._format_error_response('content required', 400)

            # Create user message
            user_msg = self._create_user_message(history.id, user_content)

            # Emit message received event
            session_id = id
            history_id = history.id
            self.emit_chat_event(session_id, history_id, 'message_received', {
                'message_id': user_msg.id,
                'role': user_msg.role,
                'content': user_msg.content_json,
                'timestamp': user_msg.created_at.isoformat()
            })

            # Emit message processing started event
            self.emit_llm_event(session_id, history_id, 'message_processing', 'Processing your message...')

            # Create EMPTY assistant message placeholder immediately
            asst_msg = self._create_assistant_placeholder(history.id)

            # Return BOTH message IDs immediately
            response_data = {
                'data': {
                    'user_message_id': user_msg.id,
                    'assistant_message_id': asst_msg.id,
                    'status': 'processing',
                    'websocket_channel': f'chat/{id}/{history.id}'
                }
            }

            # Start async processing in thread pool AFTER response
            self._submit_message_for_async_processing(
                user_msg.id, asst_msg.id, id, history.id, session.persona.id
            )

            return jsonify(response_data)
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return self._format_error_response(str(exc), 500)

    def _submit_message_for_async_processing(self, user_msg_id: int, asst_msg_id: int, session_id: int, history_id: int, persona_id: int):
        """Submit message processing to thread pool for async execution."""
        try:
            # Use the thread pool manager from the parent ChatService
            future = self.submit_async_task(
                self._process_message_async,
                user_msg_id, asst_msg_id, session_id, history_id, persona_id
            )
            
            # Log successful submission with proper logger
            self._logger.info(f"Message {user_msg_id} submitted to thread pool for async processing")
            return future
            
        except Exception as e:
            # Log error with full stack trace
            self._logger.error(f"Failed to submit message {user_msg_id} to thread pool: {e}", exc_info=True)
            # Emit error event
            self.emit_llm_event(session_id, history_id, 'processing_failed', f'Failed to start processing: {e}')
            raise

    async def _process_message_async(self, user_msg_id: int, asst_msg_id: int, 
                                    session_id: int, history_id: int, persona_id: int):
        """Process message asynchronously using streaming."""
        try:
            # Initialize handlers
            message_handler = StreamingMessageHandler(session_id, history_id)
            event_manager = StreamingEventManager(self)
            
            # Set the existing assistant message ID
            message_handler.assistant_message_id = asst_msg_id
            
            # Get model info and tools
            model_info, provider, mapping_obj = self._resolve_ai_model(persona_id)
            available_tools_info = list_persona_tools(persona_id)
            
            if not model_info or not provider or not mapping_obj:
                # No model available - mark as failed
                error_msg = "AI model, provider, or mapping not available"
                message_handler.finalize_assistant_message(error_msg)
                event_manager.emit_chunk_event(session_id, history_id, 
                                            StreamingChunk(content="", chunk_type="complete", is_final=True))
                return
            
            # Build chat history using helper method
            chat_history = self._build_chat_history(history_id, user_msg_id)
            
            # Use streaming LLM client
            try:
                async for chunk in run_chat_streaming(provider, mapping_obj, chat_history, 
                                                    available_tools_info, persona_id):
                    # Handle each chunk
                    if chunk.chunk_type == "text":
                        message_handler.update_assistant_content(chunk.content)
                        event_manager.emit_chunk_event(session_id, history_id, chunk)
                    
                    elif chunk.chunk_type == "ai_start":
                        event_manager.emit_chunk_event(session_id, history_id, chunk)
                    
                    elif chunk.chunk_type == "tool_start":
                        event_manager.emit_tool_event(session_id, history_id, 
                                                   chunk.metadata["tool_name"], "started")
                    
                    elif chunk.chunk_type == "tool_end":
                        event_manager.emit_tool_event(session_id, history_id, 
                                                   chunk.metadata["tool_name"], "completed")
                    
                    elif chunk.chunk_type == "complete":
                        message_handler.finalize_assistant_message()
                        event_manager.emit_chunk_event(session_id, history_id, chunk)
                        break
                        
            except Exception as e:
                # Handle streaming errors
                error_msg = f"Streaming error: {str(e)}"
                message_handler.finalize_assistant_message(error_msg)
                self.emit_llm_event(session_id, history_id, 'processing_failed', error_msg)
                
        except Exception as e:
            # Handle general errors
            error_msg = f"Async processing error: {str(e)}"
            self.emit_llm_event(session_id, history_id, 'processing_failed', error_msg)
            # Log the error
            if hasattr(self, '_logger'):
                self._logger.error(f"Error in _process_message_async: {e}", exc_info=True)
            else:
                print(f"Error in _process_message_async: {e}")

    @expose(
        '/sessions/{session_id}/histories/{history_id}/send', 
        methods=['POST'],
        status_codes={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "object",
                    "description": "Message content in JSON format",
                    "additionalProperties": True
                }
            },
            "required": ["content"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "history_id": {"type": "integer"},
                        "role": {"type": "string"},
                        "message_type": {"type": "string"},
                        "content_json": {"type": "object"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    def send_message_to_history(self, req: Request, session_id: int, history_id: int):
        """Send a message to a specific history within a session."""
        try:
            # Validate session and history
            session, history = self._validate_session_history(session_id, history_id)
            if not session:
                return self._format_error_response('Session not found or inactive', 404)
            if not history:
                return self._format_error_response('History not found', 404)

            # Get user content
            payload = req.get_json(silent=True) or {}
            user_content = payload.get('content')
            if not user_content:
                return self._format_error_response('content required', 400)

            # Create user message
            user_msg = self._create_user_message(history_id, user_content)

            # Update history message count
            history.message_count += 1
            db.session.commit()

            # Emit message received event
            self.emit_chat_event(session_id, history_id, 'message_received', {
                'message_id': user_msg.id,
                'role': user_msg.role,
                'content': user_msg.content_json,
                'timestamp': user_msg.created_at.isoformat()
            })

            # Emit message processing started event
            self.emit_llm_event(session_id, history_id, 'message_processing', 'Processing your message...')

            # Create EMPTY assistant message placeholder immediately
            asst_msg = self._create_assistant_placeholder(history_id)

            # Return BOTH message IDs immediately
            response_data = {
                'data': {
                    'user_message_id': user_msg.id,
                    'assistant_message_id': asst_msg.id,
                    'status': 'processing',
                    'websocket_channel': f'chat/{session_id}/{history_id}'
                }
            }

            # Start async processing in thread pool AFTER response
            self._submit_message_for_async_processing(
                user_msg.id, asst_msg.id, session_id, history_id, session.persona.id
            )

            return jsonify(response_data)
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return self._format_error_response(str(exc), 500)

    @expose(
        '/sessions/{id}/retry', 
        methods=['POST'],
        status_codes={200: 'OK', 400: 'Bad Request'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "history_id": {"type": "integer"},
                        "role": {"type": "string"},
                        "message_type": {"type": "string"},
                        "content_json": {"type": "object"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    def retry_last(self, req: Request, id: int):  # noqa: A002
        """Retry the last user message in a session."""
        try:
            last_user = ChatMessage.query.filter_by(session_id=id, role='user').order_by(ChatMessage.created_at.desc()).first()
            if not last_user:
                return self._format_error_response('No user messages', 400)
            # Reuse send logic by re-sending the last user content
            mock_req = type('obj', (), {'get_json': lambda self, silent=True: {'content': last_user.content_json}})()
            return self.send_message(mock_req, id)
        except Exception as exc:  # noqa: BLE001
            return self._format_error_response(str(exc), 500)

    @expose(
        '/sessions/{session_id}/histories/{history_id}/messages', 
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "history_id": {"type": "integer"},
                            "role": {"type": "string"},
                            "message_type": {"type": "string"},
                            "content_json": {"type": "object"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
    def list_history_messages(self, req: Request, session_id: int, history_id: int):
        """Get messages from a specific history within a session."""
        try:
            # Validate session and history
            session, history = self._validate_session_history(session_id, history_id)
            if not session:
                return self._format_error_response('Session not found or inactive', 404)
            if not history:
                return self._format_error_response('History not found', 404)

            msgs = ChatMessage.query.filter_by(history_id=history_id).order_by(ChatMessage.created_at.asc()).all()
            return jsonify({'data': [m.to_dict() for m in msgs], 'total': len(msgs)})
        except Exception as exc:  # noqa: BLE001
            return self._format_error_response(str(exc), 500)

    @expose(
        '/sessions/{session_id}/histories/{history_id}/messages/{message_id}', 
        methods=['DELETE'],
        status_codes={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "deleted_message_id": {"type": "integer"}
            }
        }
    )
    def delete_message(self, req: Request, session_id: int, history_id: int, message_id: int):
        """Delete a specific message from a history."""
        try:
            # Verify session exists and is active
            session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
            if not session:
                return self._format_error_response('Session not found or inactive', 404)

            # Verify history exists and belongs to session
            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return self._format_error_response('History not found', 404)

            # Find and delete the specific message
            message = ChatMessage.query.filter_by(id=message_id, history_id=history_id).first()
            if not message:
                return self._format_error_response('Message not found', 404)

            # Store message ID before deletion for response
            deleted_message_id = message.id
            
            # Delete the message
            db.session.delete(message)
            
            # Update history message count
            history.message_count = max(0, history.message_count - 1)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Message deleted successfully',
                'deleted_message_id': deleted_message_id
            })
            
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return self._format_error_response(str(exc), 500) 