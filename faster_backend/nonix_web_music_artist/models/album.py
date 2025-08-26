from __future__ import annotations

from sqlalchemy import Column, Date, ForeignKey, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from nonix_web_db import Base


class Album(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    title = Column(String(255), nullable=False)
    release_date = Column(Date)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    artist = relationship('Artist', foreign_keys=[artist_id], backref=backref('albums', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'title': self.title,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Album id={self.id} title={self.title!r}>"
