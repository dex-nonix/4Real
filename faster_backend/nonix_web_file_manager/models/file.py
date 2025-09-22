from __future__ import annotations
import os

from sqlalchemy import Column, ForeignKey, Integer, String, event
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
    category = relationship('FileCategory', foreign_keys=[category_id], backref=backref('files', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<File id={self.id} original={self.original_filename!r}>"


@event.listens_for(File, 'before_delete')
def delete_physical_file(mapper, connection, target):
    """Generic file cleanup - deletes physical file when database record is deleted"""
    if target.storage_url:
        try:
            file_path = target.storage_url.lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Log error but don't fail the database operation
            print(f"Warning: Could not delete physical file {file_path}: {e}")
