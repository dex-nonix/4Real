from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class AIModelMapping(db.Model):
    __tablename__ = 'ai_model_mappings'

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('ai_providers.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    parameters_json = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    provider = db.relationship('AIProvider', foreign_keys=[provider_id],
                               backref=db.backref('model_mappings', lazy=True))

    # personas relationship is handled by backref in Persona model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'name': self.name,
            'model_name': self.model_name,
            'parameters_json': self.parameters_json,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIModelMapping id={self.id} name={self.name!r} model={self.model_name!r}>"
