from __future__ import annotations

from sqlalchemy import Column, String, Text, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class ChatPrompt(BaseModel):
    __tablename__ = "chat_prompts"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    content = Column(Text)
    context = Column(JSON)

    # Relationships
    template = relationship("Template", foreign_keys=[template_id], backref=backref("chat_prompts", lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatPrompt id={self.id} name={self.name!r}>"
