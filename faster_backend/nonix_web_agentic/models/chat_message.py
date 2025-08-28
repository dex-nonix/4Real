from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from nonix_web_db import Base


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey('chat_histories.id'), nullable=False)
    role = Column(String(50), nullable=False)  # system|user|assistant|tool
    message_type = Column(String(50), nullable=False)  # text|tool_call|tool_result|image|file
    content_json = Column(JSON)  # Structured content
    status = Column(String(50), nullable=False)
    parent_message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    history = relationship('ChatHistory', foreign_keys=[history_id], backref='messages')
    parent_message = relationship('ChatMessage', foreign_keys=[parent_message_id], remote_side=[id],
                                  backref='child_messages')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'history_id': self.history_id,
            'role': self.role,
            'message_type': self.message_type,
            'status': self.status,
            'content_json': self.content_json,
            'parent_message_id': self.parent_message_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatMessage id={self.id} role={self.role!r}>"
