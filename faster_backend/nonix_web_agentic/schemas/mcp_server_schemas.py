from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field, model_validator

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    command: Optional[str] = None
    args_json: Optional[List[str]] = None
    env_json: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    transport: Optional[str] = None
    is_active: bool = True

    @model_validator(mode='after')
    def validate_transport_fields(self):
        transport = self.transport or "stdio"

        if transport == "stdio":
            if not self.command:
                raise ValueError("command is required when transport is 'stdio' or not specified")
        elif transport in ["websocket", "http"]:
            if not self.url:
                raise ValueError(f"url is required when transport is '{transport}'")

        return self


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerUpdate(BaseUpdateModel, base_model=MCPServerBase):
    pass


class MCPServerInDbModel(MCPServerBase, BaseDbModelMixin):
    pass
