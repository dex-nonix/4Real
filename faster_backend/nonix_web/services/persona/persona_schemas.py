from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from ..base_schemas import BaseDBMixin

class PersonaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    is_active: bool = True
    system_prompt: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    artist_id: Optional[int] = Field(None, gt=0)
    ai_model_mapping_id: int = Field(..., gt=0)

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(PersonaBase):
    pass

class PersonaInDB(PersonaBase, BaseDBMixin):
    pass
