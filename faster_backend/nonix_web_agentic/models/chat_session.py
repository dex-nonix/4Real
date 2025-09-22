from __future__ import annotations

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class ChatSession(BaseModel):
    __tablename__ = "chat_sessions"

    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    session_name = Column(String(255))
    session_icon = Column(String(512))
    current_history_id = Column(Integer, ForeignKey("chat_histories.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")

    # Relationships
    persona = relationship("Persona", foreign_keys=[persona_id], backref=backref("chat_sessions", lazy=True, cascade='all, delete-orphan'))
    current_history = relationship("ChatHistory", foreign_keys=[current_history_id], backref=backref("current_sessions", lazy=True, cascade='all, delete-orphan'))

    # histories relationship is handled by backref in ChatHistory model

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatSession id={self.id} title={self.session_name!r}>"
