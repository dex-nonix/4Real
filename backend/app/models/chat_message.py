from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('chat_histories.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # system|user|assistant|tool
    message_type = db.Column(db.String(50), nullable=False)  # text|tool_call|tool_result|image|file
    content_json = db.Column(db.JSON)  # Structured content
    parent_message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Relationships
    history = db.relationship('ChatHistory', foreign_keys=[history_id], backref=db.backref('messages', lazy=True))
    parent_message = db.relationship('ChatMessage', foreign_keys=[parent_message_id], remote_side=[id], backref='child_messages')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'history_id': self.history_id,
            'role': self.role,
            'message_type': self.message_type,
            'content_json': self.content_json,
            'parent_message_id': self.parent_message_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatMessage id={self.id} role={self.role!r}>"


