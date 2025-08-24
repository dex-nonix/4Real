from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from ..base_schemas import BaseDBMixin

class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    command: str = Field(..., min_length=1, max_length=512)
    args_json: Optional[Dict[str, Any]] = None
    env_json: Optional[Dict[str, Any]] = None
    is_active: bool = True

class MCPServerCreate(MCPServerBase):
    pass

class MCPServerUpdate(MCPServerBase):
    pass

class MCPServerInDB(MCPServerBase, BaseDBMixin):
    pass
