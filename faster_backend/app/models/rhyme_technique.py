from __future__ import annotations

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.sql import func

from ..database import Base


class RhymeTechnique(Base):
    __tablename__ = 'rhyme_techniques'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  
        return f"<RhymeTechnique id={self.id} name={self.name!r}>"
