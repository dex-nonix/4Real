from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class AIProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    provider_type: str = Field(..., min_length=1, max_length=50)
    module: str = Field(..., min_length=1, max_length=255)
    cls: str = Field(..., min_length=1, max_length=255)
    method: Optional[str] = Field(None, max_length=255)
    config_json: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AIProviderCreate(AIProviderBase):
    pass


class AIProviderUpdate(AIProviderBase):
    pass


class AIProviderInDbModel(AIProviderBase, BaseDbModelMixin):
    pass
