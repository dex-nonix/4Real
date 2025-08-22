from __future__ import annotations

from sqlalchemy import Boolean, Column, text, DateTime, Integer, JSON, String
from sqlalchemy.sql import func

from ..database import Base


class AIProvider(Base):
    __tablename__ = 'ai_providers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False)  # e.g., 'google', 'openai'
    module = Column(String(255), nullable=False)  # e.g., 'langchain_openai'
    cls = Column(String(255), nullable=False)  # e.g., 'ChatOpenAI'
    method = Column(String(255), nullable=True, server_default=text("'invoke'"))
    config_json = Column(JSON)
    is_active = Column(Boolean, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    # model_mappings relationship is handled by backref in AIModelMapping model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'provider_type': self.provider_type,
            'module': self.module,
            'cls': self.cls,
            'method': self.method,
            'config_json': self.config_json,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIProvider id={self.id} name={self.name!r}>"
