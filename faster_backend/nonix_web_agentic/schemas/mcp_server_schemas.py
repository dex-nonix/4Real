from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    command: str = Field(..., min_length=1, max_length=512)
    args_json: Optional[Dict[str, Any]] = None
    env_json: Optional[Dict[str, Any]] = None
    is_active: bool = True


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerUpdate(BaseUpdateModel, base_model=MCPServerBase):
    pass


class MCPServerInDbModel(MCPServerBase, BaseDbModelMixin):
    pass
