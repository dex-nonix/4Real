from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, JSON, String
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship

from nonix_web_db import BaseModel


class MCPServer(BaseModel):
    __tablename__ = 'mcp_servers'

    name = Column(String(255), unique=True, nullable=False)
    command = Column(String(512), nullable=False)
    args_json = Column(JSON)
    env_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))


    def __repr__(self) -> str:  # pragma: no cover
        return f"<MCPServer id={self.id} name={self.name!r}>"
