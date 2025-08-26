from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, text, DateTime, Integer, JSON
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from nonix_web_db import Base


class PersonaMCPServer(Base):
    __tablename__ = 'persona_mcp_servers'

    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=False)
    mcp_server_id = Column(Integer, ForeignKey('mcp_servers.id'), nullable=False)
    override_args_json = Column(JSON)
    override_env_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    persona = relationship('Persona', foreign_keys=[persona_id], backref=backref('persona_mcp_servers', lazy=True))
    mcp_server = relationship('MCPServer', foreign_keys=[mcp_server_id], backref=backref('persona_mcp_servers', lazy=True))

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
