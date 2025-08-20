from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class MCPServer(db.Model):
    __tablename__ = 'mcp_servers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    command = db.Column(db.String(512), nullable=False)
    args_json = db.Column(db.JSON)
    env_json = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'args_json': self.args_json,
            'env_json': self.env_json,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MCPServer id={self.id} name={self.name!r}>"
