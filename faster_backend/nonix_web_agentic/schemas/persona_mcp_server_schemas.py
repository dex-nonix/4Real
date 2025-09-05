from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class PersonaMCPServerBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    mcp_server_id: int = Field(..., gt=0)
    override_args_json: Optional[Dict[str, Any]] = None
    override_env_json: Optional[Dict[str, Any]] = None
    is_active: bool = True


class PersonaMCPServerCreate(PersonaMCPServerBase):
    pass


class PersonaMCPServerUpdate(BaseUpdateModel, base_model=PersonaMCPServerBase):
    pass


class PersonaMCPServerInDbModel(PersonaMCPServerBase, BaseDbModelMixin):
    pass
