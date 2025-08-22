from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from ....service_router.decorators import expose
from .....database import AsyncSessionLocal
from .....models.chat_history import ChatHistory
from .....models.chat_message import ChatMessage
from .....models.chat_session import ChatSession


class ChatHistoryMixin:
    """Mixin for chat history management operations."""

    async def _validate_session_and_history(self, db_session, session_id: int, history_id: int = None):
        """Validate session exists and optionally validate history belongs to session."""
        # Validate session
        session = await db_session.execute(
            db_session.query(ChatSession).filter_by(id=session_id, is_active=True)
        ).scalar_one_or_none()
        
        if not session:
            return None, None, JSONResponse({'error': 'Session not found or inactive'}, status_code=404)
        
        # If history_id provided, validate history too
        if history_id:
            history = await db_session.execute(
                db_session.query(ChatHistory).filter_by(id=history_id, session_id=session_id)
            ).scalar_one_or_none()
            
            if not history:
                return session, None, JSONResponse({'error': 'History not found'}, status_code=404)
            
            return session, history, None
        
        return session, None, None

    @expose(
        '/sessions/{id}/histories',
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
                            "session_id": {"type": "integer"},
                            "title": {"type": "string"},
                            "message_count": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
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
                    db_session.query(ChatHistory).filter_by(session_id=id)
                )
                histories = histories_result.scalars().all()
                
                return JSONResponse({'data': [h.to_dict() for h in histories], 'total': len(histories)})
            except Exception as exc:  # noqa: BLE001
                return JSONResponse({'error': str(exc)}, status_code=500)

    @expose(
        '/sessions/{id}/histories',
        methods=['POST'],
        status_codes={201: 'Created', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "History title"}
            }
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "session_id": {"type": "integer"},
                        "title": {"type": "string"},
                        "message_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def create_session_history(self, req: Request, payload: dict = None, id: int = None):  # noqa: A002
        """Create a new history for a specific session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session
                session, _, error_response = await self._validate_session_and_history(db_session, id)
                if error_response:
                    return error_response

                payload = payload or {}
                title = payload.get('title', 'New Conversation')

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

    @expose(
        '/sessions/{id}/histories/{history_id}',
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "session_id": {"type": "integer"},
                        "title": {"type": "string"},
                        "message_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def get_session_history(self, req: Request, id: int, history_id: int):
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

    @expose(
        '/sessions/{id}/histories/{history_id}',
        methods=['PUT'],
        status_codes={200: 'OK', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "History title"}
            }
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "session_id": {"type": "integer"},
                        "title": {"type": "string"},
                        "message_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def update_session_history(self, req: Request, payload: dict = None, id: int = None,
                                     history_id: int = None):  # noqa: A002
        """Update a specific history within a session."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history, error_response = await self._validate_session_and_history(db_session, id, history_id)
                if error_response:
                    return error_response

                data = payload or {}
                allowed_fields = ['title']

                for field in allowed_fields:
                    if field in data:
                        setattr(history, field, data[field])

                await db_session.commit()
                return JSONResponse({'data': history.to_dict()})
            except Exception as exc:  # noqa: BLE001
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, status_code=500)

    @expose(
        '/sessions/{id}/histories/{history_id}',
        methods=['DELETE'],
        status_codes={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
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

    @expose(
        '/sessions/{id}/histories/{history_id}/messages',
        methods=['DELETE'],
        status_codes={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "deleted_count": {"type": "integer"}
            }
        }
    )
    async def clear_history_messages(self, req: Request, id: int, history_id: int):
        """Clear all messages in a specific history."""
        async with AsyncSessionLocal() as db_session:
            try:
                # Validate session and history
                session, history, error_response = await self._validate_session_and_history(db_session, id, history_id)
                if error_response:
                    return error_response

                # Get count of messages to be deleted
                message_count_result = await db_session.execute(
                    db_session.query(ChatMessage).filter_by(history_id=history_id)
                )
                message_count = message_count_result.scalar()

                if message_count == 0:
                    return JSONResponse({'message': 'No messages to clear', 'deleted_count': 0})

                # Delete all messages in this history
                await db_session.execute(
                    db_session.query(ChatMessage).filter_by(history_id=history_id).delete()
                )

                # Reset message count in history
                history.message_count = 0

                await db_session.commit()

                return JSONResponse({
                    'message': f'Cleared {message_count} messages successfully',
                    'deleted_count': message_count
                })

            except Exception as exc:  # noqa: BLE001
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, status_code=500)
