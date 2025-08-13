from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # system|user|assistant|tool
    content_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    session = db.relationship('ChatSession', backref=db.backref('messages', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content_json': self.content_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatMessage id={self.id} role={self.role!r}>"


