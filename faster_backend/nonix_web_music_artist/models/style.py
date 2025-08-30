from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text

from nonix_web_db import BaseModel


class Style(BaseModel):
    __tablename__ = 'styles'

    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Style id={self.id} name={self.name!r}>"
