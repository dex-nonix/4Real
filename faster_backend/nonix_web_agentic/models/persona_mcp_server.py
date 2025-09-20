from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class PersonaMCPServer(BaseModel):
    __tablename__ = 'persona_mcp_servers'

    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=False)
    mcp_server_id = Column(Integer, ForeignKey('mcp_servers.id'), nullable=False)
    override_args_json = Column(JSON)
    override_env_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default='1')

    # Relationships
    persona = relationship('Persona', foreign_keys=[persona_id], backref=backref('persona_mcp_servers', lazy=True))
    mcp_server = relationship('MCPServer', foreign_keys=[mcp_server_id], backref=backref('persona_mcp_servers', lazy=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PersonaMCPServer id={self.id} persona_id={self.persona_id} mcp_server_id={self.mcp_server_id}>"
