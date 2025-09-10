from sqlalchemy import func, select

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from nonix_web_db import AsyncSessionLocal
from ..schemas.persona_schemas import PersonaCreate, PersonaUpdate, PersonaInDbModel
from ..models.persona import Persona
from ..models.chat_session import ChatSession


class PersonaService(BaseCrudService):
    config = CRUDConfig(
        model=Persona,
        create_schema=PersonaCreate,
        update_schema=PersonaUpdate,
        response_schema=PersonaInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'is_active', 'artist_id', 'ai_model_mapping_id']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'artist_id', 'ai_model_mapping_id', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name']
        )
    )

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

    async def list_personas_with_session_counts(self):
        """List all available personas with active session counts."""
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

        return result

    async def get_persona_with_session_count(self, persona_id: int):
        """Get a single persona by ID with active session count."""
        # Query persona with session count using JOIN
        async with AsyncSessionLocal() as db_session:
            query = self._build_persona_query(persona_id)
            result_set = await db_session.execute(query)
            result = result_set.first()

        if not result:
            raise ValueError('Persona not found')

        persona, session_count = result
        persona_data = persona.to_dict()
        persona_data['active_sessions_count'] = session_count

        return persona_data
