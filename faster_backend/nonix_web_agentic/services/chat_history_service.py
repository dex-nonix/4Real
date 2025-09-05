from sqlalchemy import select

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from nonix_web_db import AsyncSessionLocal
from nonix_web_agentic.schemas.chat_history_schemas import ChatHistoryCreate, ChatHistoryUpdate, ChatHistoryInDbModel
from ..models.chat_history import ChatHistory
from ..models.chat_session import ChatSession


class ChatHistoryService(BaseCrudService):
    config = CRUDConfig(
        model=ChatHistory,
        create_schema=ChatHistoryCreate,
        update_schema=ChatHistoryUpdate,
        response_schema=ChatHistoryInDbModel,
        filters=FilterConfig(
            allowed_fields=['session_id', 'title']
        ),
        sorting=SortingConfig(
            default_sort='updated_at',
            allowed_fields=['created_at', 'updated_at', 'title', 'message_count']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['title', 'summary'],
            display_format='{title}',
            search_fields=['title'],
            order_by='updated_at'
        )
    )

    async def _validate_session_and_history(self, db_session, session_id: int, history_id: int = None):
        """Validate session exists and optionally validate history belongs to session."""
        # Validate session
        session = (await db_session.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active)
        )).scalar_one_or_none()

        if not session:
            raise ValueError('Session not found or inactive')

        # If history_id provided, validate history too
        if history_id:
            history = (await db_session.execute(
                select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
            )).scalar_one_or_none()

            if not history:
                raise ValueError('History not found')

            return session, history

        return session, None

    async def list_session_histories(self, session_id: int):
        """List all histories for a specific session."""
        async with AsyncSessionLocal() as db_session:
            # Validate session
            await self._validate_session_and_history(db_session, session_id)

            histories_result = await db_session.execute(
                select(ChatHistory).where(ChatHistory.session_id == session_id)
            )
            histories = histories_result.scalars().all()

            return [h.to_dict() for h in histories]

    async def create_session_history(self, session_id: int, title: str = None):
        """Create a new history for a specific session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session
                await self._validate_session_and_history(db_session, session_id)

                title = title or 'New Conversation'

                history = ChatHistory(
                    session_id=session_id,
                    title=title,
                    message_count=0
                )
                db_session.add(history)
                await db_session.commit()
                await db_session.refresh(history)

                return history
            except Exception as exc:
                await db_session.rollback()
                raise exc

    async def get_session_history(self, session_id: int, history_id: int):
        """Get a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            # Validate session and history
            await self._validate_session_and_history(db_session, session_id, history_id)

            history_result = await db_session.execute(
                select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
            )
            history = history_result.scalar_one_or_none()

            if not history:
                raise ValueError('History not found')

            return history.to_dict()

    async def update_session_history(self, session_id: int, history_id: int, title: str = None):
        """Update a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history = await self._validate_session_and_history(db_session, session_id, history_id)

                if title is not None:
                    history.title = title

                await db_session.commit()
                return history
            except Exception as exc:
                await db_session.rollback()
                raise exc

    async def delete_session_history(self, session_id: int, history_id: int):
        """Delete a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history = await self._validate_session_and_history(db_session, session_id, history_id)

                # Check if this is the current history
                if session.current_history_id == history_id:
                    raise ValueError('Cannot delete current history')

                await db_session.delete(history)
                await db_session.commit()
                return {'message': 'History deleted successfully'}
            except Exception as exc:
                await db_session.rollback()
                raise exc
