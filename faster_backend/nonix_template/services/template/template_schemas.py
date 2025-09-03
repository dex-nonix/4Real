from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    parent_template_id: Optional[int] = Field(None, gt=0)


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseUpdateModel, base_model=TemplateBase):
    pass


class TemplateInDbModel(TemplateBase, BaseDbModelMixin):
    pass
