from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class PersonaMCPServer(db.Model):
    __tablename__ = 'persona_mcp_servers'

    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    mcp_server_id = db.Column(db.Integer, db.ForeignKey('mcp_servers.id'), nullable=False)
    override_args_json = db.Column(db.JSON)
    override_env_json = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    persona = db.relationship('Persona', backref=db.backref('persona_mcp_servers', lazy=True))
    mcp_server = db.relationship('MCPServer', backref=db.backref('persona_mcp_servers', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'mcp_server_id': self.mcp_server_id,
            'override_args_json': self.override_args_json,
            'override_env_json': self.override_env_json,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PersonaMCPServer id={self.id} persona_id={self.persona_id} mcp_server_id={self.mcp_server_id}>"
