from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from ..base_schemas import BaseDBMixin

class PersonaMCPServerBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    mcp_server_id: int = Field(..., gt=0)
    override_args_json: Optional[Dict[str, Any]] = None
    override_env_json: Optional[Dict[str, Any]] = None
    is_active: bool = True

class PersonaMCPServerCreate(PersonaMCPServerBase):
    pass

class PersonaMCPServerUpdate(PersonaMCPServerBase):
    pass

class PersonaMCPServerInDB(PersonaMCPServerBase, BaseDBMixin):
    pass
