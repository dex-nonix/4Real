from __future__ import annotations

from sqlalchemy import Column, ForeignKey, DateTime, Integer, JSON, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from nonix_web_db import BaseModel


class ToolInvocationLog(BaseModel):
    __tablename__ = 'tool_invocation_logs'

    history_id = Column(Integer, ForeignKey('chat_histories.id'), nullable=False)
    message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=False)
    tool_name = Column(String(255), nullable=False)
    input_json = Column(JSON)
    output_json = Column(JSON)
    status = Column(String(50), nullable=False)  # started|success|error|timeout
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)

    # Relationships
    history = relationship('ChatHistory', foreign_keys=[history_id], backref=backref('tool_logs', lazy=True))
    message = relationship('ChatMessage', foreign_keys=[message_id], backref=backref('tool_logs', lazy=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ToolInvocationLog id={self.id} tool_name={self.tool_name!r} status={self.status!r}>"
