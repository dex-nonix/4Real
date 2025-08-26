from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from nonix_web_db import Base


class Persona(Base):
    __tablename__ = 'personas'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    avatar_url = Column(String(512), nullable=True)  # NEW: Optional avatar
    is_active = Column(Boolean, nullable=False, server_default='1')
    system_prompt = Column(Text)
    metadata_json = Column(JSON)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=True)
    ai_model_mapping_id = Column(Integer, ForeignKey('ai_model_mappings.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    artist = relationship('Artist', foreign_keys=[artist_id], backref='personas')
    ai_model_mapping = relationship('AIModelMapping', foreign_keys=[ai_model_mapping_id], backref='personas')

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
