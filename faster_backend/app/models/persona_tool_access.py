from __future__ import annotations

from sqlalchemy import Boolean, relationship, DateTime, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class PersonaToolAccess(Base):
    __tablename__ = 'persona_tool_access'

    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=False)
    pattern = Column(String(255), nullable=False)
    allow = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    persona = relationship('Persona', backref=backref('tool_access', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'pattern': self.pattern,
            'allow': self.allow,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  
        return f"<PersonaToolAccess id={self.id} persona_id={self.persona_id} pattern={self.pattern!r}>"
