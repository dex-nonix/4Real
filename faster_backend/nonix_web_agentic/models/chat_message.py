from __future__ import annotations

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship

from nonix_web_db import BaseModel


class ChatMessage(BaseModel):
    __tablename__ = 'chat_messages'

    history_id = Column(Integer, ForeignKey('chat_histories.id'), nullable=False)
    role = Column(String(50), nullable=False)  # system|user|assistant|tool
    message_type = Column(String(50), nullable=False)  # text|tool_call|tool_result|image|file
    content_json = Column(JSON)  # Structured content
    status = Column(String(50), nullable=False)
    parent_message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True)

    # Relationships
    history = relationship('ChatHistory', foreign_keys=[history_id], backref='messages')
    parent_message = relationship('ChatMessage', foreign_keys=[parent_message_id], remote_side=[id],
                                  backref='child_messages')

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatMessage id={self.id} role={self.role!r}>"
