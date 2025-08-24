from __future__ import annotations

from sqlalchemy import Column, ForeignKey, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from ..database import Base


class FileLink(Base):
    __tablename__ = 'file_links'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    status = Column(String(32), nullable=False)
    comment = Column(Text)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    file = relationship('File', foreign_keys=[file_id], backref=backref('links', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'file_id': self.file_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'status': self.status,
            'comment': self.comment,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FileLink id={self.id} file_id={self.file_id} {self.entity_type}#{self.entity_id}>"
