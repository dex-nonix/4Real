from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class Album(db.Model):
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    artist = db.relationship('Artist', backref=db.backref('albums', lazy=True))

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

