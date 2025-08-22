from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ChatHistory(Base):
    __tablename__ = 'chat_histories'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    title = Column(String(255), nullable=False)  # "Chat about music", "Album discussion"
    summary = Column(Text)  # AI-generated summary
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    session = relationship('ChatSession', backref='histories')

    # messages relationship is handled by backref in ChatMessage model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'summary': self.summary,
            'message_count': self.message_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatHistory id={self.id} title={self.title!r} session_id={self.session_id}>"
