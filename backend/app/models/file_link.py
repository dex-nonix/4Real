from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class FileLink(db.Model):
    __tablename__ = 'file_links'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, index=True)
    entity_type = db.Column(db.String(64), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False)
    comment = db.Column(db.Text)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    file = db.relationship('File', backref=db.backref('links', lazy=True, cascade='all, delete-orphan'))

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
