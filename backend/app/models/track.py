from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    track_number = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    lyrics = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    album = db.relationship('Album', backref=db.backref('tracks', lazy=True))

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
