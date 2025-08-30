from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class PersonaToolAccess(BaseModel):
    __tablename__ = 'persona_tool_access'

    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=False)
    pattern = Column(String(255), nullable=False)
    allow = Column(Boolean, nullable=False, server_default='1')

    # Relationships
    persona = relationship('Persona', foreign_keys=[persona_id], backref=backref('tool_access', lazy=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PersonaToolAccess id={self.id} persona_id={self.persona_id} pattern={self.pattern!r}>"
