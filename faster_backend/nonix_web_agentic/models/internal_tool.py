from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, JSON, String, Text
from sqlalchemy.sql import text

from nonix_web_db import BaseModel


class InternalTool(BaseModel):
    __tablename__ = 'internal_tools'

    namespace = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    qualified_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    config_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InternalTool id={self.id} qualified_name={self.qualified_name!r}>"
