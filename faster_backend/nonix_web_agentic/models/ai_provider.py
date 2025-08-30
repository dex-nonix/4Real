from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, JSON, String
from sqlalchemy.sql import text

from nonix_web_db import BaseModel


class AIProvider(BaseModel):
    __tablename__ = 'ai_providers'

    name = Column(String(255), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False)  # e.g., 'google', 'openai'
    module = Column(String(255), nullable=False)  # e.g., 'langchain_openai'
    cls = Column(String(255), nullable=False)  # e.g., 'ChatOpenAI'
    method = Column(String(255), nullable=True, server_default=text("'invoke'"))
    config_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))

    # Relationships
    # model_mappings relationship is handled by backref in AIModelMapping model

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIProvider id={self.id} name={self.name!r}>"
