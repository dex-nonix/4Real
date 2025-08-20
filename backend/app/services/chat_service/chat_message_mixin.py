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
from ..llm_client import run_chat
from ..tool_runtime import build_persona_tool_map, execute_tool
from .websocket_protocol import WebSocketProtocol
from datetime import datetime
from ..tool_runtime import list_persona_tools


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
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            # Get or create current history
            if not session.current_history_id:
                history = ChatHistory(
                    session_id=id,
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
                    return jsonify({'error': 'Current history not found'}), 404

            payload = req.get_json(silent=True) or {}
            user_content = payload.get('content')
            if not user_content:
                return jsonify({'error': 'content required'}), 400

            user_msg = ChatMessage(
                history_id=history.id, 
                role='user', 
                message_type='text',
                content_json=user_content
            )
            db.session.add(user_msg)
            db.session.commit()

            # Emit message received event using protocol method
            session_id = id  # This is already available
            history_id = history.id  # This is already available
            self.emit_chat_event(session_id, history_id, 'message_received', {
                'message_id': user_msg.id,
                'role': user_msg.role,
                'content': user_msg.content_json,
                'timestamp': user_msg.created_at.isoformat()
            })

            # Emit message processing started event using protocol method
            self.emit_llm_event(session_id, history_id, 'message_processing', 'Processing your message...')

            # Resolve persona and tools
            persona = session.persona
            # Get proper tool information with schemas and descriptions
            available_tools_info = list_persona_tools(persona.id)
            available_tools = { tool['name']: {'type': 'internal'} for tool in available_tools_info }
            model_info = self._select_chat_model(persona.id)

            # Build chat history for provider call
            chat_history = []
            system_msgs = ChatMessage.query.filter_by(history_id=history.id, role='system').order_by(ChatMessage.created_at.asc()).all()
            for sm in system_msgs:
                content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
                chat_history.append({'role': 'system', 'content': content})
            user_msgs = ChatMessage.query.filter(ChatMessage.history_id==history.id, ChatMessage.id<=user_msg.id).order_by(ChatMessage.created_at.asc()).all()
            for um in user_msgs:
                role = um.role
                if role not in ('user', 'assistant'):
                    continue
                content = um.content_json if isinstance(um.content_json, dict) else {'text': str(um.content_json)}
                chat_history.append({'role': role, 'content': content})

            # Resolve model mapping and provider; fallback to placeholder if none
            assistant_output = None
            if model_info:
                provider = AIProvider.query.filter_by(id=model_info['provider_id'], is_active=True).first()
                if provider:
                    try:
                        # Reconstruct mapping object used for provider call
                        mapping_obj = AIModelMapping.query.filter_by(id=persona.ai_model_mapping_id, is_active=True).first()
                        # Pass tool information and persona_id to the LLM
                        assistant_output = run_chat(provider, mapping_obj, chat_history, available_tools_info, persona.id)
                    except Exception as exc:  # noqa: BLE001
                        assistant_output = {'type': 'text', 'text': f'Provider error: {exc}'}
            if not assistant_output:
                return jsonify({'error': 'Persona has no active model mapping or provider is unavailable'}), 400

            # If model requested a tool call, execute when allowlisted
            if isinstance(assistant_output, dict) and (assistant_output.get('type') == 'tool_call' or 'tool' in assistant_output):
                tool_name = assistant_output.get('tool')
                tool_args = assistant_output.get('args') or {}
                
                # Emit LLM tool call detected event using protocol method
                self.emit_llm_event(session_id, history_id, 'tool_call_detected', f'LLM needs to call {tool_name}')
                
                if tool_name and tool_name in available_tools:
                    # Emit tool execution started event using protocol method
                    self.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)
                    
                    log = ToolInvocationLog(
                        history_id=history.id,
                        message_id=user_msg.id,
                        tool_name=tool_name,
                        input_json=tool_args,
                        status='started'
                    )
                    db.session.add(log)
                    db.session.commit()

                    exec_result = execute_tool(persona.id, tool_name, tool_args)
                    
                    # Emit tool execution completed event using protocol method
                    self.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)
                    
                    log.status = 'success' if exec_result.get('status') == 'success' else 'error'
                    log.output_json = exec_result
                    db.session.commit()

                    # Emit LLM building response event using protocol method
                    self.emit_llm_event(session_id, history_id, 'building_response', 'LLM is building your response...')
                    
                    tool_msg = ChatMessage(
                        history_id=history.id, 
                        role='tool', 
                        message_type='tool_result',
                        content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result}
                    )
                    db.session.add(tool_msg)
                    db.session.commit()

                    # Follow-up assistant acknowledgment
                    asst_msg = ChatMessage(
                        history_id=history.id, 
                        role='assistant', 
                        message_type='text',
                        content_json={'type': 'text', 'text': 'Tool executed'}
                    )
                    db.session.add(asst_msg)
                    db.session.commit()
                    
                    # Emit response complete event using protocol method
                    self.emit_llm_event(session_id, history_id, 'response_complete', 'Response ready')
                    
                    return jsonify({'data': asst_msg.to_dict()})
                else:
                    asst_msg = ChatMessage(
                        history_id=history.id, 
                        role='assistant', 
                        message_type='text',
                        content_json={'type': 'text', 'text': f'Tool {tool_name or "(unknown)"} not allowed'}
                    )
                    db.session.add(asst_msg)
                    db.session.commit()
                    return jsonify({'data': asst_msg.to_dict()})

            # Default assistant text message
            asst_msg = ChatMessage(
                history_id=history.id, 
                role='assistant', 
                message_type='text',
                content_json=assistant_output
            )
            db.session.add(asst_msg)
            db.session.commit()

            # Emit response complete event using protocol method
            self.emit_llm_event(session_id, history_id, 'response_complete', 'Response ready')
            
            # Emit message processed event using protocol method
            self.emit_chat_event(session_id, history_id, 'message_processed', {
                'message_id': asst_msg.id,
                'status': 'processed',
                'timestamp': datetime.utcnow().isoformat()
            })

            return jsonify({'data': asst_msg.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

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
            session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            payload = req.get_json(silent=True) or {}
            user_content = payload.get('content')
            if not user_content:
                return jsonify({'error': 'content required'}), 400

            user_msg = ChatMessage(
                history_id=history_id, 
                role='user', 
                message_type='text',
                content_json=user_content
            )
            db.session.add(user_msg)
            db.session.commit()

            # Update history message count
            history.message_count += 1
            db.session.commit()

            # Resolve persona and tools
            persona = session.persona
            # Get proper tool information with schemas and descriptions
            available_tools_info = list_persona_tools(persona.id)
            available_tools = { tool['name']: {'type': 'internal'} for tool in available_tools_info }
            model_info = self._select_chat_model(persona.id)

            # Build chat history for provider call
            chat_history = []
            system_msgs = ChatMessage.query.filter_by(history_id=history_id, role='system').order_by(ChatMessage.created_at.asc()).all()
            for sm in system_msgs:
                content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
                chat_history.append({'role': 'system', 'content': content})
            user_msgs = ChatMessage.query.filter(ChatMessage.history_id==history_id, ChatMessage.id<=user_msg.id).order_by(ChatMessage.created_at.asc()).all()
            for um in user_msgs:
                role = um.role
                if role not in ('user', 'assistant'):
                    continue
                content = um.content_json if isinstance(um.content_json, dict) else {'text': str(um.content_json)}
                chat_history.append({'role': role, 'content': content})

            # Resolve model mapping and provider; fallback to placeholder if none
            assistant_output = None
            if model_info:
                provider = AIProvider.query.filter_by(id=model_info['provider_id'], is_active=True).first()
                if provider:
                    try:
                        # Reconstruct mapping object used for provider call
                        mapping_obj = AIModelMapping.query.filter_by(id=persona.ai_model_mapping_id, is_active=True).first()
                        assistant_output = run_chat(provider, mapping_obj, chat_history, available_tools_info, persona.id)
                    except Exception as exc:  # noqa: BLE001
                        assistant_output = {'type': 'text', 'text': f'Provider error: {exc}'}
            if not assistant_output:
                return jsonify({'error': 'Persona has no active model mapping or provider is unavailable'}), 400

            # If model requested a tool call, execute when allowlisted
            if isinstance(assistant_output, dict) and (assistant_output.get('type') == 'tool_call' or 'tool' in assistant_output):
                tool_name = assistant_output.get('tool')
                tool_args = assistant_output.get('args') or {}
                if tool_name and tool_name in available_tools:
                    log = ToolInvocationLog(
                        history_id=history_id,
                        message_id=user_msg.id,
                        tool_name=tool_name,
                        input_json=tool_args,
                        status='started'
                    )
                    db.session.add(log)
                    db.session.commit()

                    exec_result = execute_tool(persona.id, tool_name, tool_args)
                    log.status = 'success' if exec_result.get('status') == 'success' else 'error'
                    log.output_json = exec_result
                    db.session.commit()

                    tool_msg = ChatMessage(
                        history_id=history_id, 
                        role='tool', 
                        message_type='tool_result',
                        content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result}
                    )
                    db.session.add(tool_msg)
                    db.session.commit()

                    # Follow-up assistant acknowledgment
                    asst_msg = ChatMessage(
                        history_id=history_id, 
                        role='assistant', 
                        message_type='text',
                        content_json={'type': 'text', 'text': 'Tool executed'}
                    )
                    db.session.add(asst_msg)
                    db.session.commit()
                    return jsonify({'data': asst_msg.to_dict()})
                else:
                    asst_msg = ChatMessage(
                        history_id=history_id, 
                        role='assistant', 
                        message_type='text',
                        content_json={'type': 'text', 'text': f'Tool {tool_name or "(unknown)"} not allowed'}
                    )
                    db.session.add(asst_msg)
                    db.session.commit()
                    return jsonify({'data': asst_msg.to_dict()})

            # Default assistant text message
            asst_msg = ChatMessage(
                history_id=history_id, 
                role='assistant', 
                message_type='text',
                content_json=assistant_output
            )
            db.session.add(asst_msg)
            db.session.commit()

            # Update history message count
            history.message_count += 1
            db.session.commit()

            return jsonify({'data': asst_msg.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

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
                return jsonify({'error': 'No user messages'}), 400
            # Reuse send logic by re-sending the last user content
            mock_req = type('obj', (), {'get_json': lambda self, silent=True: {'content': last_user.content_json}})()
            return self.send_message(mock_req, id)
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

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
            session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            msgs = ChatMessage.query.filter_by(history_id=history_id).order_by(ChatMessage.created_at.asc()).all()
            return jsonify({'data': [m.to_dict() for m in msgs], 'total': len(msgs)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500 

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
                return jsonify({'error': 'Session not found or inactive'}), 404

            # Verify history exists and belongs to session
            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            # Find and delete the specific message
            message = ChatMessage.query.filter_by(id=message_id, history_id=history_id).first()
            if not message:
                return jsonify({'error': 'Message not found'}), 404

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
            return jsonify({'error': str(exc)}), 500 