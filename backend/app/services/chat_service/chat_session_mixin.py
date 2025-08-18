from __future__ import annotations

from typing import Any, Dict, List
from flask import jsonify, Request
from ...decorators import expose
from ... import db
from ...models.chat_session import ChatSession
from ...models.chat_history import ChatHistory
from ...models.persona import Persona
from ...models.chat_message import ChatMessage


class ChatSessionMixin:
    """Mixin for chat session management operations."""

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

    @expose(
        '/sessions', 
        methods=['POST'], 
        status_codes={201: 'Created', 400: 'Bad Request', 404: 'Not Found'},
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
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    def create_session(self, req: Request):
        """Create a new chat session."""
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

    @expose(
        '/sessions', 
        methods=['GET'],
        status_codes={200: 'OK'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "persona_id": {"type": "integer"},
                            "session_name": {"type": "string"},
                            "session_icon": {"type": "string"},
                            "is_active": {"type": "boolean"},
                            "current_history_id": {"type": "integer"},
                            "history_count": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
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

    @expose(
        '/sessions/{id}', 
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "history_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
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

    @expose(
        '/sessions/{id}', 
        methods=['PUT'],
        status_codes={200: 'OK', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"},
                "current_history_id": {"type": "integer", "description": "Current history ID"}
            }
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
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

    @expose(
        '/sessions/{id}', 
        methods=['DELETE'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    )
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

    @expose(
        '/personas/{persona_id}/sessions', 
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
                            "persona_id": {"type": "integer"},
                            "session_name": {"type": "string"},
                            "session_icon": {"type": "string"},
                            "is_active": {"type": "boolean"},
                            "current_history_id": {"type": "integer"},
                            "history_count": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
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

    @expose(
        '/personas/{persona_id}/start-chat', 
        methods=['POST'],
        status_codes={201: 'Created', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"}
            }
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
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