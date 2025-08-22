from __future__ import annotations

from sqlalchemy import DateTime, relationship, Integer, JSON, String
from sqlalchemy.sql import func

from ..database import Base


class ToolInvocationLog(Base):
    __tablename__ = 'tool_invocation_logs'

    id = Column(Integer, primary_key=True)
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
    history = relationship('ChatHistory', backref=backref('tool_logs', lazy=True))
    message = relationship('ChatMessage', backref=backref('tool_logs', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'history_id': self.history_id,
            'message_id': self.message_id,
            'tool_name': self.tool_name,
            'input_json': self.input_json,
            'output_json': self.output_json,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
        }

    def __repr__(self) -> str:  
        return f"<ToolInvocationLog id={self.id} tool_name={self.tool_name!r} status={self.status!r}>"
