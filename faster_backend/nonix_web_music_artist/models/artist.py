from __future__ import annotations

from sqlalchemy import Column, Date, String, Text

from nonix_web_db import BaseModel


class Artist(BaseModel):
    __tablename__ = 'artists'

    name = Column(String(255), unique=True, nullable=False)
    abbreviation = Column(String(50))
    persona = Column(Text)
    birth_date = Column(Date)

    # Relationships
    # personas relationship is handled by backref in Persona model

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Artist id={self.id} name={self.name!r}>"
