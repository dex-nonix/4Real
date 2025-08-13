from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class Persona(db.Model):
    __tablename__ = 'personas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    system_prompt = db.Column(db.Text)
    metadata_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'system_prompt': self.system_prompt,
            'metadata_json': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Persona id={self.id} name={self.name!r}>"


