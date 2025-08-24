from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from ..base_schemas import BaseDBMixin

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

class AIModelMappingInDB(AIModelMappingBase, BaseDBMixin):
    pass
