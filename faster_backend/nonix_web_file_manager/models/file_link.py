from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class FileLink(BaseModel):
    __tablename__ = 'file_links'

    file_id = Column(Integer, ForeignKey('files.id'), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    status = Column(String(32), nullable=False)
    comment = Column(Text)
    sort_order = Column(Integer, nullable=False, default=0)

    # Relationships
    file = relationship('File', foreign_keys=[file_id], backref=backref('links', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FileLink id={self.id} file_id={self.file_id} {self.entity_type}#{self.entity_id}>"
