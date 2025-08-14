from __future__ import annotations

from typing import Any, Dict, List

from flask import jsonify, Request

from ..decorators import expose
from .. import db
from ..models.chat_session import ChatSession
from ..models.chat_message import ChatMessage
from ..models.persona import Persona
from ..models.internal_tool import InternalTool
from ..models.persona_tool_access import PersonaToolAccess
from ..models.persona_mcp_server import PersonaMCPServer
from ..models.mcp_server import MCPServer
from ..models.ai_model_mapping import AIModelMapping
from ..models.tool_invocation_log import ToolInvocationLog
from .llm_client import run_chat
from .internal_tool_registry import registry as internal_tool_registry


class ChatService:
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

    # Endpoints
    @expose('/sessions', methods=['POST'])
    def create_session(self, req: Request):
        try:
            payload = req.get_json(silent=True) or {}
            persona_id = int(payload.get('persona_id'))
            title = payload.get('title') or 'New Chat'
            created_by = payload.get('created_by')
            metadata_json = payload.get('metadata')

            persona = Persona.query.filter_by(id=persona_id, is_active=True).first()
            if not persona:
                return jsonify({'error': 'Persona not found or inactive'}), 404

            session = ChatSession(persona_id=persona_id, title=title, created_by=created_by, metadata_json=metadata_json)
            db.session.add(session)
            db.session.commit()

            # Optional initial system message from persona.system_prompt
            if persona.system_prompt:
                sys_msg = ChatMessage(session_id=session.id, role='system', content_json={'type': 'system', 'text': persona.system_prompt})
                db.session.add(sys_msg)
                db.session.commit()

            return jsonify({'data': session.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions', methods=['GET'])
    def list_sessions(self, req: Request):
        try:
            persona_id = req.args.get('persona_id')
            created_by = req.args.get('created_by')

            query = ChatSession.query
            if persona_id:
                query = query.filter_by(persona_id=int(persona_id))
            if created_by:
                query = query.filter_by(created_by=created_by)

            items = query.order_by(ChatSession.created_at.desc()).all()
            return jsonify({'data': [s.to_dict() for s in items], 'total': len(items)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}', methods=['GET'])
    def get_session(self, req: Request, id: int):  # noqa: A002 - API name
        try:
            session = ChatSession.query.filter_by(id=id).first()
            if not session:
                return jsonify({'error': 'Not found'}), 404
            return jsonify({'data': session.to_dict()})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}/messages', methods=['GET'])
    def list_messages(self, req: Request, id: int):  # noqa: A002
        try:
            session = ChatSession.query.filter_by(id=id).first()
            if not session:
                return jsonify({'error': 'Not found'}), 404

            msgs = ChatMessage.query.filter_by(session_id=id).order_by(ChatMessage.created_at.asc()).all()
            return jsonify({'data': [m.to_dict() for m in msgs], 'total': len(msgs)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/sessions/{id}/send', methods=['POST'])
    def send_message(self, req: Request, id: int):  # noqa: A002
        try:
            session = ChatSession.query.filter_by(id=id).first()
            if not session:
                return jsonify({'error': 'Not found'}), 404

            payload = req.get_json(silent=True) or {}
            user_content = payload.get('content')
            if not user_content:
                return jsonify({'error': 'content required'}), 400

            user_msg = ChatMessage(session_id=id, role='user', content_json=user_content)
            db.session.add(user_msg)
            db.session.commit()

            # Resolve persona and tools
            persona = session.persona
            available_tools = self._resolve_persona_tools(persona.id)
            model_info = self._select_chat_model(persona.id)

            # Build chat history for provider call
            history = []
            system_msgs = ChatMessage.query.filter_by(session_id=id, role='system').order_by(ChatMessage.created_at.asc()).all()
            for sm in system_msgs:
                content = sm.content_json if isinstance(sm.content_json, dict) else {'text': str(sm.content_json)}
                history.append({'role': 'system', 'content': content})
            user_msgs = ChatMessage.query.filter(ChatMessage.session_id==id, ChatMessage.id<=user_msg.id).order_by(ChatMessage.created_at.asc()).all()
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
                        session_id=id,
                        message_id=user_msg.id,
                        tool_name=tool_name,
                        input_json=tool_args,
                        status='started'
                    )
                    db.session.add(log)
                    db.session.commit()

                    exec_result = internal_tool_registry.execute(tool_name, tool_args)
                    log.status = 'success' if exec_result.get('status') == 'success' else 'error'
                    log.output_json = exec_result
                    db.session.commit()

                    tool_msg = ChatMessage(session_id=id, role='tool', content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result})
                    db.session.add(tool_msg)
                    db.session.commit()

                    # Follow-up assistant acknowledgment
                    asst_msg = ChatMessage(session_id=id, role='assistant', content_json={'type': 'text', 'text': 'Tool executed'})
                    db.session.add(asst_msg)
                    db.session.commit()
                    return jsonify({'data': asst_msg.to_dict()})
                else:
                    asst_msg = ChatMessage(session_id=id, role='assistant', content_json={'type': 'text', 'text': f'Tool {tool_name or "(unknown)"} not allowed'})
                    db.session.add(asst_msg)
                    db.session.commit()
                    return jsonify({'data': asst_msg.to_dict()})

            # Default assistant text message
            asst_msg = ChatMessage(session_id=id, role='assistant', content_json=assistant_output)
            db.session.add(asst_msg)
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

    @expose('/personas/{persona_id}/tools', methods=['GET'])
    def persona_tools(self, req: Request, persona_id: int):
        try:
            persona = Persona.query.filter_by(id=persona_id).first()
            if not persona:
                return jsonify({'error': 'Not found'}), 404
            tools = self._resolve_persona_tools(persona.id)
            return jsonify({'data': sorted(list(tools.keys()))})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/personas/{persona_id}/tools/execute', methods=['POST'])
    def persona_tool_execute(self, req: Request, persona_id: int):
        try:
            payload = req.get_json(silent=True) or {}
            tool_name = payload.get('tool')
            tool_args = payload.get('args') or {}
            session_id = payload.get('session_id')
            user_message_id = payload.get('message_id')

            persona = Persona.query.filter_by(id=persona_id).first()
            if not persona:
                return jsonify({'error': 'Not found'}), 404
            allow = self._resolve_persona_tools(persona.id)
            if tool_name not in allow:
                return jsonify({'error': 'Tool not allowed'}), 403

            log = ToolInvocationLog(
                session_id=session_id,
                message_id=user_message_id,
                tool_name=tool_name,
                input_json=tool_args,
                status='started'
            )
            db.session.add(log)
            db.session.commit()

            exec_result = internal_tool_registry.execute(tool_name, tool_args)
            log.status = 'success' if exec_result.get('status') == 'success' else 'error'
            log.output_json = exec_result
            db.session.commit()

            if session_id:
                tool_msg = ChatMessage(session_id=session_id, role='tool', content_json={'type': 'tool_result', 'tool': tool_name, 'input': tool_args, 'output': exec_result})
                db.session.add(tool_msg)
                db.session.commit()

            return jsonify({'data': exec_result})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/mcp/servers/status', methods=['GET'])
    def mcp_status(self, req: Request):
        try:
            servers = MCPServer.query.all()
            return jsonify({'data': [s.to_dict() for s in servers]})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500


