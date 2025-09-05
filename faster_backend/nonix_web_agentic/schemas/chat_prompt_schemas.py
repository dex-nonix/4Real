from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class ChatPromptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_id: Optional[int] = Field(None, gt=0)
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatPromptCreate(ChatPromptBase):
    pass


class ChatPromptUpdate(BaseUpdateModel, base_model=ChatPromptBase):
    pass


class ChatPromptInDbModel(ChatPromptBase, BaseDbModelMixin):
    pass
