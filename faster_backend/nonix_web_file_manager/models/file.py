from __future__ import annotations

from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from nonix_web_db import Base


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship('FileCategory', foreign_keys=[category_id], backref=backref('files', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'category_id': self.category_id,
            'title': self.title,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'storage_url': self.storage_url,
            'sha256': self.sha256,
            'width': self.width,
            'height': self.height,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<File id={self.id} original={self.original_filename!r}>"
