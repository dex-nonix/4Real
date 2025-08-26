from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class AIModelMappingBase(BaseModel):
    provider_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    model_name: str = Field(..., min_length=1, max_length=255)
    parameters_json: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AIModelMappingCreate(AIModelMappingBase):
    pass


class AIModelMappingUpdate(AIModelMappingBase):
    pass


class AIModelMappingInDbModel(AIModelMappingBase, BaseDbModelMixin):
    pass
