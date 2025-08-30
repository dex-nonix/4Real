from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import text

from nonix_web_db import BaseModel


class AIModelMapping(BaseModel):
    __tablename__ = 'ai_model_mappings'

    provider_id = Column(Integer, ForeignKey('ai_providers.id'), nullable=False)
    name = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    parameters_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))

    # Relationships
    provider = relationship('AIProvider', foreign_keys=[provider_id], backref=backref('model_mappings', lazy=True))

    # personas relationship is handled by backref in Persona model

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIModelMapping id={self.id} name={self.name!r} model={self.model_name!r}>"
