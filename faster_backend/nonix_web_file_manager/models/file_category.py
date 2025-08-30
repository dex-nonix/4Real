from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text

from nonix_web_db import BaseModel


class FileCategory(BaseModel):
    __tablename__ = 'file_categories'

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FileCategory id={self.id} name={self.name!r}>"
