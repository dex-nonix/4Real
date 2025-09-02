from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class ToolInvocationLogBase(BaseModel):
    history_id: int = Field(..., gt=0)
    message_id: int = Field(..., gt=0)
    tool_name: str = Field(..., min_length=1, max_length=255)
    input_json: Optional[Dict[str, Any]] = None
    output_json: Optional[Dict[str, Any]] = None
    status: str = Field(..., min_length=1, max_length=50)
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = Field(None, ge=0)
    seq: Optional[int] = Field(None, ge=1)
    turn_id: Optional[str] = Field(None, max_length=64)
    run_id: Optional[str] = Field(None, max_length=64)
    parent_ids: Optional[List[str]] = None
    tool_run_id: Optional[str] = Field(None, max_length=64)


class ToolInvocationLogCreate(ToolInvocationLogBase):
    pass


class ToolInvocationLogUpdate(ToolInvocationLogBase):
    pass


class ToolInvocationLogInDbModel(ToolInvocationLogBase, BaseDbModelMixin):
    pass
