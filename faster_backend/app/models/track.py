from __future__ import annotations

from sqlalchemy import Column, ForeignKey, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from ..database import Base


class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, ForeignKey('albums.id'), nullable=False)
    title = Column(String(255), nullable=False)
    track_number = Column(Integer)
    duration_seconds = Column(Integer)
    lyrics = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    album = relationship('Album', backref=backref('tracks', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'album_id': self.album_id,
            'title': self.title,
            'track_number': self.track_number,
            'duration_seconds': self.duration_seconds,
            'lyrics': self.lyrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Track id={self.id} title={self.title!r}>"
