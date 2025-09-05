from sqlalchemy import func, select

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from nonix_web_db import AsyncSessionLocal
from nonix_web_agentic.schemas.chat_session_schemas import ChatSessionCreate, ChatSessionUpdate, ChatSessionInDbModel
from ..models.chat_session import ChatSession
from ..models.chat_history import ChatHistory
from ..models.persona import Persona


class ChatSessionService(BaseCrudService):
    config = CRUDConfig(
        model=ChatSession,
        create_schema=ChatSessionCreate,
        update_schema=ChatSessionUpdate,
        response_schema=ChatSessionInDbModel,
        filters=FilterConfig(
            allowed_fields=['persona_id', 'session_name', 'session_icon', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='created_at',
            allowed_fields=['created_at', 'updated_at', 'session_name']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['session_name', 'session_icon'],
            display_format='{session_name}',
            search_fields=['session_name'],
            order_by='created_at'
        )
    )

    async def _get_persona_by_id(self, db_session, persona_id: int):
        """Get persona by ID with validation."""
        persona_stmt = select(Persona).where(Persona.id == persona_id, Persona.is_active)
        persona_result = await db_session.execute(persona_stmt)
        persona = persona_result.scalar_one_or_none()
        if not persona:
            raise ValueError('Persona not found or inactive')
        return persona

    async def _get_session_by_id(self, db_session, session_id: int):
        """Get session by ID with validation."""
        session_stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active)
        session_result = await db_session.execute(session_stmt)
        session = session_result.scalar_one_or_none()
        if not session:
            raise ValueError('Session not found or inactive')
        return session

    async def _get_sessions_with_history_counts(self, persona_id: int = None, session_id: int = None):
        """Utility method to get sessions with history counts using single JOIN query."""

        async with AsyncSessionLocal() as db_session:
            # Build the query using select
            stmt = select(
                ChatSession,
                func.count(ChatHistory.id).label('history_count')
            ).outerjoin(
                ChatHistory, ChatSession.id == ChatHistory.session_id
            ).where(
                ChatSession.is_active
            )

            if persona_id:
                stmt = stmt.where(ChatSession.persona_id == persona_id)
            if session_id:
                stmt = stmt.where(ChatSession.id == session_id)

            stmt = stmt.group_by(ChatSession.id)

            result = await db_session.execute(stmt)
            return result

    async def create_session_with_history(self, persona_id: int, session_name: str = None, session_icon: str = None):
        """Create a new chat session with initial history."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Get persona first to check if exists and get name
                persona = await self._get_persona_by_id(db_session, persona_id)

                session_name = session_name or f'Chat with {persona.name}'
                session_icon = session_icon

                session = ChatSession(
                    persona_id=persona_id,
                    session_name=session_name,
                    session_icon=session_icon,
                    is_active=True
                )
                db_session.add(session)
                await db_session.commit()
                await db_session.refresh(session)

                # Create initial history for the session
                history = ChatHistory(
                    session_id=session.id,
                    title='New Conversation',
                    message_count=0
                )
                db_session.add(history)
                await db_session.commit()
                await db_session.refresh(history)

                # Set this as the current history
                session.current_history_id = history.id
                await db_session.commit()

                return session
            except Exception as exc:
                await db_session.rollback()
                raise exc

    async def get_sessions_with_counts(self, persona_id: int = None):
        """Get all sessions with history counts."""
        # Use utility method for single JOIN query with COUNT
        sessions_result = await self._get_sessions_with_history_counts(persona_id=persona_id)
        sessions_with_counts = sessions_result.all()

        result = []
        for session, history_count in sessions_with_counts:
            session_data = session.to_dict()
            session_data['history_count'] = history_count  # Just the count, no objects
            result.append(session_data)
        return result

    async def get_session_with_count(self, session_id: int):
        """Get a specific session by ID with history count."""
        # Use utility method for single JOIN query with COUNT
        sessions_result = await self._get_sessions_with_history_counts(session_id=session_id)
        session_with_count = sessions_result.first()

        if not session_with_count:
            raise ValueError('Session not found')

        session, history_count = session_with_count
        session_data = session.to_dict()
        session_data['history_count'] = history_count  # Just the count, no objects

        return session_data

    async def update_session(self, session_id: int, session_name: str = None, session_icon: str = None, is_active: bool = None):
        """Update a chat session."""
        async with AsyncSessionLocal() as db_session:
            try:
                session = await self._get_session_by_id(db_session, session_id)

                if session_name is not None:
                    session.session_name = session_name
                if session_icon is not None:
                    session.session_icon = session_icon
                if is_active is not None:
                    session.is_active = is_active

                await db_session.commit()
                return session
            except Exception as exc:
                await db_session.rollback()
                raise exc

    async def delete_session(self, session_id: int):
        """Delete a chat session (soft delete by setting is_active=False)."""
        async with AsyncSessionLocal() as db_session:
            try:
                session = await self._get_session_by_id(db_session, session_id)

                session.is_active = False
                await db_session.commit()
                return {'message': 'Session deleted successfully'}
            except Exception as exc:
                await db_session.rollback()
                raise exc

    async def get_persona_sessions(self, persona_id: int):
        """Get all sessions for a specific persona."""
        async with AsyncSessionLocal() as db_session:
            await self._get_persona_by_id(db_session, persona_id)

            # Use utility method for single JOIN query with COUNT
            sessions_result = await self._get_sessions_with_history_counts(persona_id=persona_id)
            sessions_with_counts = sessions_result.all()

            sessions_data = []
            for session, history_count in sessions_with_counts:
                session_data = session.to_dict()
                session_data['history_count'] = history_count  # Just the count, no objects
                sessions_data.append(session_data)

            return sessions_data

    async def start_chat_with_persona(self, persona_id: int, session_name: str = None, session_icon: str = None):
        """Start a new chat session with a persona."""
        return await self.create_session_with_history(persona_id, session_name, session_icon)
