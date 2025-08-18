from __future__ import annotations

from typing import Any, Dict, List

from flask import jsonify, Request

from ..decorators import expose
from .. import db
from ..models.chat_session import ChatSession
from ..models.chat_message import ChatMessage
from ..models.chat_history import ChatHistory
from ..models.persona import Persona
from ..models.internal_tool import InternalTool
from ..models.persona_tool_access import PersonaToolAccess
from ..models.persona_mcp_server import PersonaMCPServer
from ..models.mcp_server import MCPServer
from ..models.ai_model_mapping import AIModelMapping
from ..models.tool_invocation_log import ToolInvocationLog
from .llm_client import run_chat
from .tool_runtime import build_persona_tool_map, execute_tool, list_persona_tools
from .base_api_service import BaseApiService


class ChatService(BaseApiService):
    """Simple chat endpoints handling session lifecycle and message send."""

    # Helpers
    def _resolve_persona_tools(self, persona_id: int) -> Dict[str, Any]:
        tools: Dict[str, Any] = {}

        active_tools: List[InternalTool] = InternalTool.query.filter_by(is_active=True).all()
        patterns: List[PersonaToolAccess] = PersonaToolAccess.query.filter_by(persona_id=persona_id, allow=True).all()

        def matches(pattern: str, name: str) -> bool:
            if pattern.endswith(':*'):
                return name.startswith(pattern[:-2] + ':')
            return pattern == name

        for tool in active_tools:
            qname = tool.qualified_name
            if any(matches(p.pattern, qname) for p in patterns):
                tools[qname] = {'type': 'internal'}

        # Include MCP tools under serverName:toolName when needed (lazy discovery placeholder)
        return tools

    def _select_chat_model(self, persona_id: int) -> Dict[str, Any] | None:
        # Strict persona selection: require persona.ai_model_mapping_id
        from ..models.persona import Persona
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

    def _get_sessions_with_history_counts(self, persona_id: int = None, session_id: int = None):
        """Utility method to get sessions with history counts using single JOIN query."""
        from sqlalchemy import func
        
        query = db.session.query(
            ChatSession,
            func.count(ChatHistory.id).label('history_count')
        ).outerjoin(
            ChatHistory, ChatSession.id == ChatHistory.session_id
        ).filter(
            ChatSession.is_active == True
        )
        
        if persona_id:
            query = query.filter(ChatSession.persona_id == persona_id)
        if session_id:
            query = query.filter(ChatSession.id == session_id)
            
        return query.group_by(ChatSession.id)

    # Endpoints
    @expose(
        '/sessions', 
        methods=['POST'], 
        status_codes={201: 'Created', 400: 'Bad Request'},
        # 🚀 NEW: Define request/response types in decorator
        request_schema={
            "type": "object",
            "properties": {
                "persona_id": {"type": "integer", "description": "Persona ID"},
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"}
            },
            "required": ["persona_id"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "persona_id": {"type": "integer"},
                "session_name": {"type": "string"},
                "is_active": {"type": "boolean"}
            }
        }
    )
    def create_session(self, req: Request):
        try:
            payload = req.get_json(silent=True) or {}
            persona_id = int(payload.get('persona_id'))
            session_name = payload.get('session_name') or f'Chat with {Persona.query.get(persona_id).name if Persona.query.get(persona_id) else "Persona"}'
            session_icon = payload.get('session_icon')

            persona = Persona.query.filter_by(id=persona_id, is_active=True).first()
            if not persona:
                return jsonify({'error': 'Persona not found or inactive'}), 404

            session = ChatSession(
                persona_id=persona_id, 
                session_name=session_name, 
                session_icon=session_icon,
                is_active=True
            )
            db.session.add(session)
            db.session.commit()

            # Create initial history for the session
            history = ChatHistory(
                session_id=session.id,
                title='New Conversation',
                message_count=0
            )
            db.session.add(history)
            db.session.commit()

            # Set this as the current history
            session.current_history_id = history.id
            db.session.commit()

            # Optional initial system message from persona.system_prompt
            if persona.system_prompt:
                sys_msg = ChatMessage(
                    history_id=history.id, 
                    role='system', 
                    message_type='text',
                    content_json={'type': 'system', 'text': persona.system_prompt}
                )
                db.session.add(sys_msg)
                db.session.commit()

            return jsonify({'data': session.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500



    @expose('/sessions/{id}/messages', methods=['GET'])
    def list_messages(self, req: Request, id: int):  # noqa: A002
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

    @expose('/sessions/{id}/send', methods=['POST'])
    def send_message(self, req: Request, id: int):  # noqa: A002
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

            # Resolve persona and tools
            persona = session.persona
            available_tools = { name: {'type': 'internal'} for name in build_persona_tool_map(persona.id).keys() }
            model_info = self._select_chat_model(persona.id)

            # Build chat history for provider call
            history = []
            system_msgs = ChatMessage.query.filter_by(history_id=history.id, role='system').order_by(ChatMessage.created_at.asc()).all()
            for sm in system_msgs:
                content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
                history.append({'role': 'system', 'content': content})
            user_msgs = ChatMessage.query.filter(ChatMessage.history_id==history.id, ChatMessage.id<=user_msg.id).order_by(ChatMessage.created_at.asc()).all()
            for um in user_msgs:
                role = um.role
                if role not in ('user', 'assistant'):
                    continue
                content = um.content_json if isinstance(um.content_json, dict) else {'text': str(um.content_json)}
                history.append({'role': role, 'content': content})

            # Resolve model mapping and provider; fallback to placeholder if none
            assistant_output = None
            if model_info:
                from ..models.ai_provider import AIProvider
                provider = AIProvider.query.filter_by(id=model_info['provider_id'], is_active=True).first()
                if provider:
                    try:
                        # Reconstruct mapping object used for provider call
                        mapping_obj = AIModelMapping.query.filter_by(id=persona.ai_model_mapping_id, is_active=True).first()
                        assistant_output = run_chat(provider, mapping_obj, history)
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
                        history_id=history.id,
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
                    return jsonify({'data': asst_msg.to_dict()})
                else:
                    asst_msg = ChatMessage(session_id=id, role='assistant', content_json={'type': 'text', 'text': f'Tool {tool_name or "(unknown)"} not allowed'})
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

            return jsonify({'data': asst_msg.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{session_id}/histories/{history_id}/send', methods=['POST'])
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
            available_tools = { name: {'type': 'internal'} for name in build_persona_tool_map(persona.id).keys() }
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
                from ..models.ai_provider import AIProvider
                provider = AIProvider.query.filter_by(id=model_info['provider_id'], is_active=True).first()
                if provider:
                    try:
                        # Reconstruct mapping object used for provider call
                        mapping_obj = AIModelMapping.query.filter_by(id=persona.ai_model_mapping_id, is_active=True).first()
                        assistant_output = run_chat(provider, mapping_obj, chat_history)
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

    @expose('/sessions/{id}/retry', methods=['POST'])
    def retry_last(self, req: Request, id: int):  # noqa: A002
        try:
            last_user = ChatMessage.query.filter_by(session_id=id, role='user').order_by(ChatMessage.created_at.desc()).first()
            if not last_user:
                return jsonify({'error': 'No user messages'}), 400
            # Reuse send logic by re-sending the last user content
            mock_req = type('obj', (), {'get_json': lambda self, silent=True: {'content': last_user.content_json}})()
            return self.send_message(mock_req, id)
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/personas', methods=['GET'])
    def list_personas(self, req: Request):
        """List all available personas with their active sessions and histories."""
        try:
            personas = Persona.query.filter_by(is_active=True).all()
            result = []
            for persona in personas:
                persona_data = persona.to_dict()
                # Use utility method for single JOIN query with COUNT
                sessions_with_counts = self._get_sessions_with_history_counts(persona_id=persona.id).all()
                
                sessions_data = []
                for session, history_count in sessions_with_counts:
                    session_data = session.to_dict()
                    session_data['history_count'] = history_count  # Just the count, no objects
                    sessions_data.append(session_data)
                persona_data['sessions'] = sessions_data
                result.append(persona_data)
            return jsonify({'data': result, 'total': len(result)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/personas/{persona_id}/sessions', methods=['GET'])
    def get_persona_sessions(self, req: Request, persona_id: int):
        """Get all sessions for a specific persona."""
        try:
            persona = Persona.query.filter_by(id=persona_id, is_active=True).first()
            if not persona:
                return jsonify({'error': 'Persona not found or inactive'}), 404

            # Use utility method for single JOIN query with COUNT
            sessions_with_counts = self._get_sessions_with_history_counts(persona_id=persona_id).all()
            
            sessions_data = []
            for session, history_count in sessions_with_counts:
                session_data = session.to_dict()
                session_data['history_count'] = history_count  # Just the count, no objects
                sessions_data.append(session_data)
            
            return jsonify({'data': sessions_data, 'total': len(sessions_data)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/personas/{persona_id}/start-chat', methods=['POST'])
    def start_chat_with_persona(self, req: Request, persona_id: int):
        """Start a new chat session with a persona."""
        try:
            persona = Persona.query.filter_by(id=persona_id, is_active=True).first()
            if not persona:
                return jsonify({'error': 'Persona not found or inactive'}), 404

            payload = req.get_json(silent=True) or {}
            session_name = payload.get('session_name') or f'Chat with {persona.name}'
            session_icon = payload.get('session_icon')

            # Create new session
            session = ChatSession(
                persona_id=persona_id,
                session_name=session_name,
                session_icon=session_icon,
                is_active=True
            )
            db.session.add(session)
            db.session.commit()

            # Create initial history
            history = ChatHistory(
                session_id=session.id,
                title='New Conversation',
                message_count=0
            )
            db.session.add(history)
            db.session.commit()

            # Set as current history
            session.current_history_id = history.id
            db.session.commit()

            # Add system message if persona has one
            if persona.system_prompt:
                sys_msg = ChatMessage(
                    history_id=history.id,
                    role='system',
                    message_type='text',
                    content_json={'type': 'system', 'text': persona.system_prompt}
                )
                db.session.add(sys_msg)
                db.session.commit()

            return jsonify({'data': session.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/personas/{persona_id}/tools', methods=['GET'])
    def persona_tools(self, req: Request, persona_id: int):
        try:
            persona = Persona.query.filter_by(id=persona_id).first()
            if not persona:
                return jsonify({'error': 'Not found'}), 404
            return jsonify({'data': list_persona_tools(persona.id)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/personas/{persona_id}/tools/execute', methods=['POST'])
    def persona_tool_execute(self, req: Request, persona_id: int):
        try:
            payload = req.get_json(silent=True) or {}
            tool_name = payload.get('tool')
            tool_args = payload.get('args') or {}
            history_id = payload.get('history_id')
            user_message_id = payload.get('message_id')

            persona = Persona.query.filter_by(id=persona_id).first()
            if not persona:
                return jsonify({'error': 'Not found'}), 404
            tools = build_persona_tool_map(persona.id)
            if tool_name not in tools:
                return jsonify({'error': 'Tool not allowed'}), 403

            log = ToolInvocationLog(
                history_id=history_id,
                message_id=user_message_id,
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

            if history_id:
                tool_msg = ChatMessage(history_id=history_id, role='tool', message_type='tool_result', content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result})
                db.session.add(tool_msg)
                db.session.commit()

            return jsonify({'data': exec_result})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{session_id}/histories/{history_id}/messages', methods=['GET'])
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

    @expose('/mcp/servers/status', methods=['GET'])
    def mcp_status(self, req: Request):
        try:
            servers = MCPServer.query.all()
            return jsonify({'data': [s.to_dict() for s in servers]})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    # ADDITIONAL ENDPOINTS NEEDED FOR FULL UI SUPPORT
    
    @expose('/sessions', methods=['GET'])
    def list_sessions(self, req: Request):
        """List all active chat sessions."""
        try:
            # Use utility method for single JOIN query with COUNT
            sessions_with_counts = self._get_sessions_with_history_counts().all()
            
            result = []
            for session, history_count in sessions_with_counts:
                session_data = session.to_dict()
                session_data['history_count'] = history_count  # Just the count, no objects
                result.append(session_data)
            return jsonify({'data': result, 'total': len(result)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}', methods=['GET'])
    def get_session(self, req: Request, id: int):  # noqa: A002
        """Get a specific chat session by ID."""
        try:
            # Use utility method for single JOIN query with COUNT
            session_with_count = self._get_sessions_with_history_counts(session_id=id).first()
            
            if not session_with_count:
                return jsonify({'error': 'Session not found or inactive'}), 404
            
            session, history_count = session_with_count
            session_data = session.to_dict()
            session_data['history_count'] = history_count  # Just the count, no objects
            
            return jsonify({'data': session_data})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}', methods=['PUT'])
    def update_session(self, req: Request, id: int):  # noqa: A002
        """Update a chat session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            data = req.get_json(silent=True) or {}
            allowed_fields = ['session_name', 'session_icon', 'current_history_id']
            
            for field in allowed_fields:
                if field in data:
                    setattr(session, field, data[field])
            
            db.session.commit()
            return jsonify({'data': session.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}', methods=['DELETE'])
    def delete_session(self, req: Request, id: int):  # noqa: A002
        """Delete a chat session (soft delete by setting is_active=False)."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            session.is_active = False
            db.session.commit()
            return jsonify({'message': 'Session deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}/histories', methods=['GET'])
    def list_session_histories(self, req: Request, id: int):  # noqa: A002
        """List all histories for a specific session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            histories = ChatHistory.query.filter_by(session_id=id).all()
            return jsonify({'data': [h.to_dict() for h in histories], 'total': len(histories)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}/histories', methods=['POST'])
    def create_session_history(self, req: Request, id: int):  # noqa: A002
        """Create a new history for a specific session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            payload = req.get_json(silent=True) or {}
            title = payload.get('title', 'New Conversation')

            history = ChatHistory(
                session_id=id,
                title=title,
                message_count=0
            )
            db.session.add(history)
            db.session.commit()

            return jsonify({'data': history.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}/histories/{history_id}', methods=['PUT'])
    def update_session_history(self, req: Request, id: int, history_id: int):  # noqa: A002
        """Update a specific history within a session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            data = req.get_json(silent=True) or {}
            allowed_fields = ['title']
            
            for field in allowed_fields:
                if field in data:
                    setattr(history, field, data[field])
            
            db.session.commit()
            return jsonify({'data': history.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}/histories/{history_id}', methods=['DELETE'])
    def delete_session_history(self, req: Request, id: int, history_id: int):  # noqa: A002
        """Delete a specific history within a session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            # Check if this is the current history
            if session.current_history_id == history_id:
                return jsonify({'error': 'Cannot delete current history'}), 400

            db.session.delete(history)
            db.session.commit()
            return jsonify({'message': 'History deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500


