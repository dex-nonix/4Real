from pydantic import BaseModel, Field
from typing import Optional
from ..base_schemas import BaseDBMixin

class ChatHistoryBase(BaseModel):
    session_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = None
    message_count: int = Field(default=0, ge=0)

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistoryUpdate(ChatHistoryBase):
    pass

class ChatHistoryInDB(ChatHistoryBase, BaseDBMixin):
    pass
