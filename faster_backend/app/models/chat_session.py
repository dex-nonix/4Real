from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'),
                           nullable=False) 
    session_name = db.Column(db.String(255))
    session_icon = db.Column(db.String(512)) 
    current_history_id = db.Column(db.Integer, db.ForeignKey('chat_histories.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    persona = db.relationship('Persona', foreign_keys=[persona_id], backref=db.backref('chat_sessions', lazy=True))
    current_history = db.relationship('ChatHistory', foreign_keys=[current_history_id])

    # histories relationship is handled by backref in ChatHistory model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'session_name': self.session_name,
            'session_icon': self.session_icon,
            'current_history_id': self.current_history_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatSession id={self.id} title={self.title!r}>"
