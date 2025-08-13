from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class ToolInvocationLog(db.Model):
    __tablename__ = 'tool_invocation_logs'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'))
    tool_name = db.Column(db.String(255), nullable=False)
    input_json = db.Column(db.JSON)
    output_json = db.Column(db.JSON)
    status = db.Column(db.String(50), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)

    session = db.relationship('ChatSession', backref=db.backref('tool_logs', lazy=True))
    message = db.relationship('ChatMessage', backref=db.backref('tool_logs', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_id': self.message_id,
            'tool_name': self.tool_name,
            'input_json': self.input_json,
            'output_json': self.output_json,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ToolInvocationLog id={self.id} tool_name={self.tool_name!r} status={self.status!r}>"


