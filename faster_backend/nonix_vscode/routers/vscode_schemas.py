from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class VscodeStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"


class VscodeWorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    workspace_path: str = Field(..., min_length=1)
    port: int = Field(..., gt=0, le=65535)
    host: Optional[str] = Field("localhost", max_length=255)
    status: VscodeStatus = Field(VscodeStatus.STOPPED)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    auto_restart: Optional[bool] = Field(True)
    max_restarts: Optional[int] = Field(3, ge=0)


class VscodeWorkspaceCreate(VscodeWorkspaceBase):
    pass


class VscodeWorkspaceUpdate(BaseUpdateModel, base_model=VscodeWorkspaceBase):
    pass


class VscodeWorkspaceInDbModel(VscodeWorkspaceBase, BaseDbModelMixin):
    pass
