from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class Persona(db.Model):
    __tablename__ = 'personas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    avatar_url = db.Column(db.String(512), nullable=True)  # NEW: Optional avatar
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    system_prompt = db.Column(db.Text)
    metadata_json = db.Column(db.JSON)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=True)
    ai_model_mapping_id = db.Column(db.Integer, db.ForeignKey('ai_model_mappings.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    artist = db.relationship('Artist', foreign_keys=[artist_id], backref=db.backref('personas', lazy=True))
    ai_model_mapping = db.relationship('AIModelMapping', foreign_keys=[ai_model_mapping_id],
                                       backref=db.backref('personas', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'system_prompt': self.system_prompt,
            'metadata_json': self.metadata_json,
            'artist_id': self.artist_id,
            'ai_model_mapping_id': self.ai_model_mapping_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Persona id={self.id} name={self.name!r}>"
