from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.sql import func

from ..database import Base


class MCPServer(Base):
    __tablename__ = 'mcp_servers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    command = Column(String(512), nullable=False)
    args_json = Column(JSON)
    env_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

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

    def __repr__(self) -> str:  
        return f"<MCPServer id={self.id} name={self.name!r}>"
