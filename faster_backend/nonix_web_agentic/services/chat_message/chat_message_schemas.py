from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class ChatMessageBase(BaseModel):
    history_id: int = Field(..., gt=0)
    role: str = Field(..., min_length=1, max_length=50)
    message_type: str = Field(..., min_length=1, max_length=50)
    content_json: Optional[Dict[str, Any]] = None
    status: str = Field(..., min_length=1, max_length=50)
    parent_message_id: Optional[int] = Field(None, gt=0)


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageUpdate(ChatMessageBase):
    pass


class ChatMessageInDbModel(ChatMessageBase, BaseDbModelMixin):
    pass
