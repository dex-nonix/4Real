from __future__ import annotations

from typing import Any, Dict, List

from flask import jsonify, Request

from ..decorators import expose
from .. import db
from ..models.chat_history import ChatHistory
from ..models.chat_session import ChatSession
from ..models.persona import Persona


class ChatHistoryService:
    """Service for managing chat histories within sessions."""

    @expose('/chat-sessions/{session_id}/histories', methods=['GET'])
    def list_histories(self, req: Request, session_id: int):
        """List all histories for a specific session."""
        try:
            session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            histories = ChatHistory.query.filter_by(session_id=session_id).order_by(ChatHistory.updated_at.desc()).all()
            return jsonify({'data': [h.to_dict() for h in histories], 'total': len(histories)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/chat-sessions/{session_id}/histories', methods=['POST'])
    def create_history(self, req: Request, session_id: int):
        """Create a new history within a session."""
        try:
            session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            payload = req.get_json(silent=True) or {}
            title = payload.get('title', 'New Conversation')
            summary = payload.get('summary')

            history = ChatHistory(
                session_id=session_id,
                title=title,
                summary=summary,
                message_count=0
            )
            db.session.add(history)
            db.session.commit()

            # Update session to point to new history if it's the first one
            if not session.current_history_id:
                session.current_history_id = history.id
                db.session.commit()

            return jsonify({'data': history.to_dict()}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/chat-sessions/{session_id}/histories/{history_id}', methods=['GET'])
    def get_history(self, req: Request, session_id: int, history_id: int):
        """Get a specific history within a session."""
        try:
            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404
            return jsonify({'data': history.to_dict()})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    @expose('/chat-sessions/{session_id}/histories/{history_id}', methods=['PUT'])
    def update_history(self, req: Request, session_id: int, history_id: int):
        """Update a history (rename, update summary)."""
        try:
            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            payload = req.get_json(silent=True) or {}
            if 'title' in payload:
                history.title = payload['title']
            if 'summary' in payload:
                history.summary = payload['summary']

            db.session.commit()
            return jsonify({'data': history.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/chat-sessions/{session_id}/histories/{history_id}', methods=['DELETE'])
    def delete_history(self, req: Request, session_id: int, history_id: int):
        """Delete a history and all its messages."""
        try:
            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            # Check if this is the current history for the session
            session = ChatSession.query.filter_by(id=session_id).first()
            if session and session.current_history_id == history_id:
                # Set current_history_id to None or another history
                session.current_history_id = None
                db.session.commit()

            db.session.delete(history)
            db.session.commit()
            return jsonify({'message': 'History deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    @expose('/chat-sessions/{session_id}/histories/{history_id}/activate', methods=['POST'])
    def activate_history(self, req: Request, session_id: int, history_id: int):
        """Set a history as the current active history for a session."""
        try:
            session = ChatSession.query.filter_by(id=session_id, is_active=True).first()
            if not session:
                return jsonify({'error': 'Session not found or inactive'}), 404

            history = ChatHistory.query.filter_by(id=history_id, session_id=session_id).first()
            if not history:
                return jsonify({'error': 'History not found'}), 404

            session.current_history_id = history_id
            db.session.commit()

            return jsonify({'data': session.to_dict()})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500
