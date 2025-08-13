from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class InternalTool(db.Model):
    __tablename__ = 'internal_tools'

    id = db.Column(db.Integer, primary_key=True)
    namespace = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    qualified_name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    config_json = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'namespace': self.namespace,
            'name': self.name,
            'qualified_name': self.qualified_name,
            'description': self.description,
            'config_json': self.config_json,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InternalTool id={self.id} qualified_name={self.qualified_name!r}>"


