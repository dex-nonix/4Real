from pydantic import BaseModel, Field
from typing import Optional
from ..base_schemas import BaseDBMixin

class ChatSessionBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    session_name: Optional[str] = Field(None, max_length=255)
    session_icon: Optional[str] = Field(None, max_length=512)
    current_history_id: Optional[int] = Field(None, gt=0)
    is_active: bool = True

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(ChatSessionBase):
    pass

class ChatSessionInDB(ChatSessionBase, BaseDBMixin):
    pass
