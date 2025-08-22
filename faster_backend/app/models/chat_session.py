from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id'),
                        nullable=False)  # NOT unique - multiple sessions per persona
    session_name = Column(String(255))  # NEW: Optional custom name
    session_icon = Column(String(512))  # NEW: Optional custom icon
    current_history_id = Column(Integer, ForeignKey('chat_histories.id'), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='1')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    persona = relationship('Persona', backref='chat_sessions')
    current_history = relationship('ChatHistory')

    # histories relationship is handled by backref in ChatHistory model

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'session_name': self.session_name,
            'session_icon': self.session_icon,
            'current_history_id': self.current_history_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatSession id={self.id} title={self.title!r}>"
