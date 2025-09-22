from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class Persona(BaseModel):
    __tablename__ = 'personas'

    name = Column(String(255), unique=True, nullable=False)
    avatar_url = Column(String(512), nullable=True)  # NEW: Optional avatar
    is_active = Column(Boolean, nullable=False, server_default='1')
    system_prompt = Column(Text)
    metadata_json = Column(JSON)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=True)
    ai_model_mapping_id = Column(Integer, ForeignKey('ai_model_mappings.id'), nullable=False)

    # Relationships
    artist = relationship('Artist', foreign_keys=[artist_id], backref=backref('personas', lazy=True, cascade='all, delete-orphan'))
    ai_model_mapping = relationship('AIModelMapping', foreign_keys=[ai_model_mapping_id], backref=backref('personas', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Persona id={self.id} name={self.name!r}>"
