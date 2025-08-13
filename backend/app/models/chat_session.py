from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.String(255))
    metadata_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    persona = db.relationship('Persona', backref=db.backref('chat_sessions', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'title': self.title,
            'created_by': self.created_by,
            'metadata_json': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatSession id={self.id} title={self.title!r}>"


