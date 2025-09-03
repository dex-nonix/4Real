from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

import nonix_web.services.web_server_router
from nonix_web_db import AsyncSessionLocal
from .models_and_schemas import (
    HistoryListResponse,
    CreateHistoryRequest,
    HistoryResponse,
    HistoryWithMessagesResponse,
    UpdateHistoryRequest,
    DeleteHistoryResponse,
    MessageListResponse
)
from ....models.chat_history import ChatHistory
from ....models.chat_message import ChatMessage
from ....models.chat_session import ChatSession


class ChatHistoryMixin:
    """Mixin for chat history management operations."""

    async def _validate_session_and_history(self, db_session, session_id: int, history_id: int = None):
        """Validate session exists and optionally validate history belongs to session."""
        # Validate session
        session = (await db_session.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True)
        )).scalar_one_or_none()

        if not session:
            return None, None, JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

        # If history_id provided, validate history too
        if history_id:
            history = (await db_session.execute(
                select(ChatHistory).where(ChatHistory.id == history_id, ChatHistory.session_id == session_id)
            )).scalar_one_or_none()

            if not history:
                return session, None, JSONResponse({'error': 'History not found'}, status_code=404)

            return session, history, None

        return session, None, None

    @nonix_web.services.base_service.route(
        '/sessions/{id}/histories',
        methods=['GET'],
        response_model=HistoryListResponse
    )
    async def list_session_histories(self, req: Request, id: int):  # noqa: A002
        """List all histories for a specific session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session
                session, _, error_response = await self._validate_session_and_history(db_session, id)
                if error_response:
                    return error_response

                histories_result = await db_session.execute(
                    select(ChatHistory).where(ChatHistory.session_id == id)
                )
                histories = histories_result.scalars().all()

                return JSONResponse({'data': [h.to_dict() for h in histories], 'total': len(histories)})
            except Exception as exc:  # noqa: BLE001
                return JSONResponse({'error': str(exc)}, status_code=500)

    @nonix_web.services.base_service.route(
        '/sessions/{id}/histories',
        methods=['POST'],
        response_model=HistoryResponse
    )
    async def create_session_history(self, req: Request, payload: CreateHistoryRequest, id: int = None):  # noqa: A002
        """Create a new history for a specific session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session
                session, _, error_response = await self._validate_session_and_history(db_session, id)
                if error_response:
                    return error_response

                title = payload.title or 'New Conversation'

                history = ChatHistory(
                    session_id=id,
                    title=title,
                    message_count=0
                )
                db_session.add(history)
                await db_session.commit()
                await db_session.refresh(history)

                return JSONResponse({'data': history.to_dict()}, status_code=201)
            except Exception as exc:  # noqa: BLE001
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, status_code=500)

    @nonix_web.services.base_service.route(
        '/sessions/{id}/histories/{history_id}',
        methods=['GET'],
        response_model=HistoryWithMessagesResponse
    )
    async def get_session_history(self, req: Request, id: int, history_id: int):  # noqa: A002
        """Get a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history, error_response = await self._validate_session_and_history(db_session, id, history_id)
                if error_response:
                    return error_response

                return JSONResponse({'data': history.to_dict()})
            except Exception as exc:
                return JSONResponse({'error': str(exc)}, status_code=500)

    @nonix_web.services.base_service.route(
        '/sessions/{id}/histories/{history_id}',
        methods=['PUT'],
        response_model=HistoryResponse
    )
    async def update_session_history(self, req: Request, payload: UpdateHistoryRequest, id: int,
                                     history_id: int):  # noqa: A002
        """Update a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history, error_response = await self._validate_session_and_history(db_session, id, history_id)
                if error_response:
                    return error_response

                if payload.title is not None:
                    history.title = payload.title

                await db_session.commit()
                return JSONResponse({'data': history.to_dict()})
            except Exception as exc:  # noqa: BLE001
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, status_code=500)

    @nonix_web.services.base_service.route(
        '/sessions/{id}/histories/{history_id}',
        methods=['DELETE'],
        response_model=DeleteHistoryResponse
    )
    async def delete_session_history(self, req: Request, id: int, history_id: int):  # noqa: A002
        """Delete a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history, error_response = await self._validate_session_and_history(db_session, id, history_id)
                if error_response:
                    return error_response

                # Check if this is the current history
                if session.current_history_id == history_id:
                    return JSONResponse({'error': 'Cannot delete current history'}, status_code=400)

                await db_session.delete(history)
                await db_session.commit()
                return JSONResponse({'message': 'History deleted successfully'})
            except Exception as exc:  # noqa: BLE001
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, status_code=500)

    
