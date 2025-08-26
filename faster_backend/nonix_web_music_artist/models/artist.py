from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from nonix_web_db import Base


class Artist(Base):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    abbreviation = Column(String(50))
    persona = Column(Text)
    birth_date = Column(Date)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    # personas relationship is handled by backref in Persona model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'persona': self.persona,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Artist id={self.id} name={self.name!r}>"
