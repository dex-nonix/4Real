from __future__ import annotations

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class Album(BaseModel):
    __tablename__ = 'albums'

    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    title = Column(String(255), nullable=False)
    release_date = Column(Date)
    description = Column(Text)

    # Relationships
    artist = relationship('Artist', foreign_keys=[artist_id], backref=backref('albums', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Album id={self.id} title={self.title!r}>"
