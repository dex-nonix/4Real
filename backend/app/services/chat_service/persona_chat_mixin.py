from __future__ import annotations

from typing import Any, Dict, List
from flask import jsonify, Request
from ...decorators import expose
from ... import db
from ...models.persona import Persona
from ...models.chat_session import ChatSession
from ...models.chat_history import ChatHistory
from ...models.chat_message import ChatMessage


class PersonaChatMixin:
    """Mixin for persona-related chat operations."""

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
        '/personas', 
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
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "system_prompt": {"type": "string"},
                            "ai_model_mapping_id": {"type": "integer"},
                            "is_active": {"type": "boolean"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"},
                            "sessions": {
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
                            }
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
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