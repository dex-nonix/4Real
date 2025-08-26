from typing import Optional

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class ChatHistoryBase(BaseModel):
    session_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = None
    message_count: int = Field(default=0, ge=0)


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistoryUpdate(ChatHistoryBase):
    pass


class ChatHistoryInDbModel(ChatHistoryBase, BaseDbModelMixin):
    pass
