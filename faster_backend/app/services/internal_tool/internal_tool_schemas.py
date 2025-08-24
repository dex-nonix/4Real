from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from ..base_schemas import BaseDBMixin

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

class InternalToolInDB(InternalToolBase, BaseDBMixin):
    pass
