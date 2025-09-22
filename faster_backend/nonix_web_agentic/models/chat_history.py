from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class ChatHistory(BaseModel):
    __tablename__ = 'chat_histories'

    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    title = Column(String(255), nullable=False)  # "Chat about music", "Album discussion"
    summary = Column(Text)  # AI-generated summary
    message_count = Column(Integer, default=0)

    # Relationships
    session = relationship('ChatSession', foreign_keys=[session_id], backref=backref('histories', lazy=True, cascade='all, delete-orphan'))

    # messages relationship is handled by backref in ChatMessage model

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatHistory id={self.id} title={self.title!r} session_id={self.session_id}>"
