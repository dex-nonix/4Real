from __future__ import annotations

from typing import Any, Dict, List
from flask import jsonify, Request
from ...decorators import expose
from ... import db
from ...models.chat_session import ChatSession
from ...models.chat_history import ChatHistory


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
    def list_session_histories(self, req: Request, id: int):  # noqa: A002
        """List all histories for a specific session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            histories = ChatHistory.query.filter_by(session_id=id).all()
            return jsonify({'data': [h.to_dict() for h in histories], 'total': len(histories)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

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
    def create_session_history(self, req: Request, id: int):  # noqa: A002
        """Create a new history for a specific session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            payload = req.get_json(silent=True) or {}
            title = payload.get('title', 'New Conversation')

            history = ChatHistory(
                session_id=id,
                title=title,
                message_count=0
            )
            db.session.add(history)
            db.session.commit()

            return jsonify({'data': history.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

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
    def update_session_history(self, req: Request, id: int, history_id: int):  # noqa: A002
        """Update a specific history within a session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            data = req.get_json(silent=True) or {}
            allowed_fields = ['title']
            
            for field in allowed_fields:
                if field in data:
                    setattr(history, field, data[field])
            
            db.session.commit()
            return jsonify({'data': history.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

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
    def delete_session_history(self, req: Request, id: int, history_id: int):  # noqa: A002
        """Delete a specific history within a session."""
        try:
            session = ChatSession.query.filter_by(id=id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            # Check if this is the current history
            if session.current_history_id == history_id:
                return jsonify({'error': 'Cannot delete current history'}), 400

            db.session.delete(history)
            db.session.commit()
            return jsonify({'message': 'History deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500 