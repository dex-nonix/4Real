from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class File(BaseModel):
    __tablename__ = 'files'

    category_id = Column(Integer, ForeignKey('file_categories.id'))
    title = Column(String(255))
    original_filename = Column(String(512), nullable=False)
    mime_type = Column(String(255), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    storage_url = Column(String(1024), nullable=False)
    sha256 = Column(String(64))
    width = Column(Integer)
    height = Column(Integer)
    duration_seconds = Column(Integer)

    # Relationships
    category = relationship('FileCategory', foreign_keys=[category_id], backref=backref('files', lazy=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<File id={self.id} original={self.original_filename!r}>"
