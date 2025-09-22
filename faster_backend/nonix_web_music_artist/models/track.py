from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class Track(BaseModel):
    __tablename__ = 'tracks'

    album_id = Column(Integer, ForeignKey('albums.id'), nullable=False)
    title = Column(String(255), nullable=False)
    track_number = Column(Integer)
    duration_seconds = Column(Integer)
    lyrics = Column(Text)

    # Relationships
    album = relationship('Album', foreign_keys=[album_id], backref=backref('tracks', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Track id={self.id} title={self.title!r}>"
