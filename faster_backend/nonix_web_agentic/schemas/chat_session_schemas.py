from typing import Optional

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class ChatSessionBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    session_name: Optional[str] = Field(None, max_length=255)
    session_icon: Optional[str] = Field(None, max_length=512)
    current_history_id: Optional[int] = Field(None, gt=0)
    is_active: bool = True


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseUpdateModel, base_model=ChatSessionBase):
    pass


class ChatSessionInDbModel(ChatSessionBase, BaseDbModelMixin):
    pass
