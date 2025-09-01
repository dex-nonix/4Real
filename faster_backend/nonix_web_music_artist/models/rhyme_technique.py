from __future__ import annotations

from sqlalchemy import Column, String, Text

from nonix_web_db import BaseModel


class RhymeTechnique(BaseModel):
    __tablename__ = 'rhyme_techniques'

    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RhymeTechnique id={self.id} name={self.name!r}>"
