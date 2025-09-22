from __future__ import annotations
from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, DateTime
from nonix_web_db import BaseModel


class VscodeWorkspace(BaseModel):
    __tablename__ = 'vscode_workspaces'

    name = Column(String(255), unique=True, nullable=False)
    workspace_path = Column(Text, nullable=False)
    port = Column(Integer, nullable=False)
    host = Column(String(255), default="localhost")
    status = Column(String(50), default="stopped")
    config = Column(JSON, default={})

    auto_restart = Column(Boolean, default=True)
    max_restarts = Column(Integer, default=3)
    restart_count = Column(Integer, default=0)
    last_crash = Column(String(500))
    crash_time = Column(DateTime)
    started_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<VscodeWorkspace id={self.id} name={self.name!r}>"
