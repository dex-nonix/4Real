from __future__ import annotations

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from .... import db
from ....api.service_router.decorators import expose
from ....models.chat_history import ChatHistory
from ....models.chat_message import ChatMessage
from ....models.chat_session import ChatSession


class ChatHistoryMixin:
    """Mixin for chat history management operations."""

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
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

            histories = ChatHistory.query.filter_by(session_id=id).all()
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
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

            payload = payload or {}
            title = payload.get('title', 'New Conversation')

            history = ChatHistory(
                session_id=id,
                title=title,
                message_count=0
            )
            db.session.add(history)
            db.session.commit()

            return JSONResponse({'data': history.to_dict()}, status_code=201)
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
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
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return JSONResponse({'error': 'History not found'}, status_code=404)

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
    async def update_session_history(self, req: Request, payload: dict = None, id: int = None, history_id: int = None):  # noqa: A002
        """Update a specific history within a session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return JSONResponse({'error': 'History not found'}, status_code=404)

            data = payload or {}
            allowed_fields = ['title']

            for field in allowed_fields:
                if field in data:
                    setattr(history, field, data[field])

            db.session.commit()
            return JSONResponse({'data': history.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
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
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return JSONResponse({'error': 'History not found'}, status_code=404)

            # Check if this is the current history
            if session.current_history_id == history_id:
                return JSONResponse({'error': 'Cannot delete current history'}, status_code=400)

            db.session.delete(history)
            db.session.commit()
            return JSONResponse({'message': 'History deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
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
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return JSONResponse({'error': 'Session not found or inactive'}, status_code=404)

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return JSONResponse({'error': 'History not found'}, status_code=404)

            # Get count of messages to be deleted
            message_count = ChatMessage.query.filter_by(history_id=history_id).count()

            if message_count == 0:
                return JSONResponse({'message': 'No messages to clear', 'deleted_count': 0})

            # Delete all messages in this history
            ChatMessage.query.filter_by(history_id=history_id).delete()

            # Reset message count in history
            history.message_count = 0

            db.session.commit()

            return JSONResponse({
                'message': f'Cleared {message_count} messages successfully',
                'deleted_count': message_count
            })

        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return JSONResponse({'error': str(exc)}, status_code=500)
