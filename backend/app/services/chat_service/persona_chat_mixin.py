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
        """List all available personas - FLAT STRUCTURE, NO NESTING."""
        try:
            personas = Persona.query.filter_by(is_active=True).all()
            result = []
            for persona in personas:
                # Return only persona data - NO nested sessions!
                persona_data = persona.to_dict()
                result.append(persona_data)
            return jsonify({'data': result, 'total': len(result)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500 