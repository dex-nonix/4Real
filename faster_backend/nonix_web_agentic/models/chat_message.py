from __future__ import annotations

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

from nonix_web_db import BaseModel


class ChatMessage(BaseModel):
    __tablename__ = 'chat_messages'
    __table_args__ = (
        Index('ix_chat_messages_history_seq', 'history_id', 'seq', unique=True),
        Index('ix_chat_messages_turn_id', 'turn_id'),
    )

    history_id = Column(Integer, ForeignKey('chat_histories.id'), nullable=False)
    role = Column(String(50), nullable=False)  # system|user|assistant|tool
    message_type = Column(String(50), nullable=False)  # text|tool_call|tool_result|image|file
    content_json = Column(JSON)  # Structured content
    status = Column(String(50), nullable=False)
    seq = Column(Integer, nullable=False)
    turn_id = Column(String(64), nullable=False)
    run_id = Column(String(64))
    parent_ids = Column(JSON)
    tool_run_id = Column(String(64))

    # Relationships
    history = relationship('ChatHistory', foreign_keys=[history_id], backref='messages')

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatMessage id={self.id} role={self.role!r}>"

    def to_dict(self) -> dict:
        data = super().to_dict()
        # Flatten tool fields for tool messages into top-level keys
        if self.message_type in ('tool_call', 'tool_result') and isinstance(self.content_json, dict):
            data['tool_name'] = self.content_json.get('tool_name')
            data['tool_args'] = self.content_json.get('tool_args')
            data['execution_status'] = self.content_json.get('execution_status')
            data['result'] = self.content_json.get('result')
            data['executed_by'] = self.content_json.get('executed_by')
            data['execution_time'] = self.content_json.get('execution_time')
            data['execution_path'] = self.content_json.get('execution_path')
        return data
