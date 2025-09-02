from __future__ import annotations

from sqlalchemy import Column, Integer

from nonix_web_db import Base


class MessageSequence(Base):
    __tablename__ = 'message_sequences'

    history_id = Column(Integer, primary_key=True)
    next_seq = Column(Integer, nullable=False, default=1)


