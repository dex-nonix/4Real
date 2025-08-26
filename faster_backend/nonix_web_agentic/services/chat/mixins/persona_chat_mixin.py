from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select

from nonix_web.services.base_service import route
from nonix_web_db import AsyncSessionLocal
from .models_and_schemas import (
    PersonaListResponse,
    PersonaChatResponse
)
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

    def _build_persona_query(self, persona_id: int = None):
        """Build base query for personas with session counts."""
        query = select(
            Persona,
            func.count(ChatSession.id).label('session_count')
        ).outerjoin(
            ChatSession,
            (Persona.id == ChatSession.persona_id) & (ChatSession.is_active == True)
        ).where(
            Persona.is_active == True
        )

        if persona_id is not None:
            query = query.where(Persona.id == persona_id)

        return query.group_by(Persona.id)

    @route(
        '/personas',
        methods=['GET'],
        response_model=PersonaListResponse
    )
    async def list_personas(self, req: Request):
        """List all available personas with active session counts."""
        try:
            # Query personas with session counts using JOIN
            async with AsyncSessionLocal() as db_session:
                query = self._build_persona_query()
                result_set = await db_session.execute(query)
                personas_with_counts = result_set.all()

            result = []
            for persona, session_count in personas_with_counts:
                # Get persona data and add session count
                persona_data = persona.to_dict()
                persona_data['active_sessions_count'] = session_count
                result.append(persona_data)

            return JSONResponse({'data': result, 'total': len(result)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, status_code=500)

    @route(
        '/personas/{persona_id:int}',
        methods=['GET'],
        response_model=PersonaChatResponse
    )
    async def get_persona(self, req: Request, persona_id: int):
        """Get a single persona by ID with active session count."""
        try:
            # Query persona with session count using JOIN
            async with AsyncSessionLocal() as db_session:
                query = self._build_persona_query(persona_id)
                result_set = await db_session.execute(query)
                result = result_set.first()

            if not result:
                return JSONResponse({'error': 'Persona not found'}, status_code=404)

            persona, session_count = result
            persona_data = persona.to_dict()
            persona_data['active_sessions_count'] = session_count

            return JSONResponse(persona_data)
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, status_code=500)
