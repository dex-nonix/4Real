from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class InternalToolBase(BaseModel):
    namespace: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    qualified_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None
    is_active: bool = True


class InternalToolCreate(InternalToolBase):
    pass


class InternalToolUpdate(InternalToolBase):
    pass


class InternalToolInDbModel(InternalToolBase, BaseDbModelMixin):
    pass
