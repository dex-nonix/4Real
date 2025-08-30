from __future__ import annotations

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class ChatMessageBase(BaseModel):
    history_id: int = Field(..., gt=0)
    role: str = Field(..., max_length=50)
    message_type: str = Field(..., max_length=50)
    content_json: Optional[Dict[str, Any]] = None
    status: str = Field(..., max_length=50)


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageUpdate(ChatMessageBase):
    pass


class ChatMessageInDbModel(ChatMessageBase, BaseDbModelMixin):
    pass
