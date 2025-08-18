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
                            "avatar_url": {"type": "string"},
                            "description": {"type": "string"},
                            "system_prompt": {"type": "string"},
                            "ai_model_mapping_id": {"type": "integer"},
                            "artist_id": {"type": "integer"},
                            "is_active": {"type": "boolean"},
                            "metadata_json": {"type": "object"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
    def list_personas(self, req: Request):
        """List all available personas with active session counts."""
        try:
            # Use INNER JOIN to get personas with their active session counts
            from sqlalchemy import func
            
            # Query personas with session counts using JOIN
            personas_with_counts = db.session.query(
                Persona,
                func.count(ChatSession.id).label('session_count')
            ).outerjoin(
                ChatSession, 
                (Persona.id == ChatSession.persona_id) & (ChatSession.is_active == True)
            ).filter(
                Persona.is_active == True
            ).group_by(
                Persona.id
            ).all()
            
            result = []
            for persona, session_count in personas_with_counts:
                # Get persona data and add session count
                persona_data = persona.to_dict()
                persona_data['active_sessions_count'] = session_count
                result.append(persona_data)
                
            return jsonify({'data': result, 'total': len(result)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500 