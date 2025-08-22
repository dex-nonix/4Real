from __future__ import annotations

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func

from .... import db
from ....api.service_router.decorators import expose
from ....models.chat_session import ChatSession
from ....models.persona import Persona


class PersonaChatMixin:
    """Mixin for persona-related chat operations."""

    # Reusable schema for persona responses
    PERSONA_SCHEMA = {
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
            "updated_at": {"type": "string", "format": "date-time"},
            "active_sessions_count": {"type": "integer"}
        }
    }

    async def _build_persona_query(self, persona_id: int = None):
        """Build base query for personas with session counts."""
        query = db.session.query(
            Persona,
            func.count(ChatSession.id).label('session_count')
        ).outerjoin(
            ChatSession,
            (Persona.id == ChatSession.persona_id) & (ChatSession.is_active == True)
        ).filter(
            Persona.is_active == True
        )

        if persona_id is not None:
            query = query.filter(Persona.id == persona_id)

        return query.group_by(Persona.id)

    @expose(
        '/personas',
        methods=['GET'],
        status_codes={200: 'OK'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": PERSONA_SCHEMA
                },
                "total": {"type": "integer"}
            }
        }
    )
    async def list_personas(self, req: Request):
        """List all available personas with active session counts."""
        try:
            # Query personas with session counts using JOIN
            query = await self._build_persona_query()
            personas_with_counts = query.all()

            result = []
            for persona, session_count in personas_with_counts:
                # Get persona data and add session count
                persona_data = persona.to_dict()
                persona_data['active_sessions_count'] = session_count
                result.append(persona_data)

            return JSONResponse({'data': result, 'total': len(result)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, status_code=500)

    @expose(
        '/personas/{int:persona_id}',
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema=PERSONA_SCHEMA
    )
    async def get_persona_by_id(self, req: Request, persona_id: int):
        """Get a single persona by ID with active session count."""
        try:
            # Query persona with session count using JOIN
            query = await self._build_persona_query(persona_id)
            result = query.first()

            if not result:
                return JSONResponse({'error': 'Persona not found'}, status_code=404)

            persona, session_count = result
            persona_data = persona.to_dict()
            persona_data['active_sessions_count'] = session_count

            return JSONResponse(persona_data)
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, status_code=500)
