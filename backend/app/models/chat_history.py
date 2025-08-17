from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class ChatHistory(db.Model):
    __tablename__ = 'chat_histories'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)  # "Chat about music", "Album discussion"
    summary = db.Column(db.Text)  # AI-generated summary
    message_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    session = db.relationship('ChatSession', foreign_keys=[session_id], backref=db.backref('histories', lazy=True))
    # messages relationship is handled by backref in ChatMessage model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'summary': self.summary,
            'message_count': self.message_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatHistory id={self.id} title={self.title!r} session_id={self.session_id}>"
