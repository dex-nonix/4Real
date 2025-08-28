from __future__ import annotations

from sqlalchemy import Boolean, Column, text, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func

from nonix_web_db import Base


class InternalTool(Base):
    __tablename__ = 'internal_tools'

    id = Column(Integer, primary_key=True)
    namespace = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    qualified_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    config_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

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
