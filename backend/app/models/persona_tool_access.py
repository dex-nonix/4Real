from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class PersonaToolAccess(db.Model):
    __tablename__ = 'persona_tool_access'

    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    pattern = db.Column(db.String(255), nullable=False)
    allow = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    persona = db.relationship('Persona', backref=db.backref('tool_access', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'pattern': self.pattern,
            'allow': self.allow,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PersonaToolAccess id={self.id} persona_id={self.persona_id} pattern={self.pattern!r}>"


