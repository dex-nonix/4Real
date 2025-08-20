from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('file_categories.id'))
    title = db.Column(db.String(255))
    original_filename = db.Column(db.String(512), nullable=False)
    mime_type = db.Column(db.String(255), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    storage_url = db.Column(db.String(1024), nullable=False)
    sha256 = db.Column(db.String(64))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    category = db.relationship('FileCategory', backref=db.backref('files', lazy=True))

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
