from datetime import datetime
from typing import Optional, Any, Dict

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


class ToolInvocationLogCreate(ToolInvocationLogBase):
    pass


class ToolInvocationLogUpdate(ToolInvocationLogBase):
    pass


class ToolInvocationLogInDbModel(ToolInvocationLogBase, BaseDbModelMixin):
    pass
