from pydantic import BaseModel, Field
from ..base_schemas import BaseDBMixin

class PersonaToolAccessBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    pattern: str = Field(..., min_length=1, max_length=255)
    allow: bool = True

class PersonaToolAccessCreate(PersonaToolAccessBase):
    pass

class PersonaToolAccessUpdate(PersonaToolAccessBase):
    pass

class PersonaToolAccessInDB(PersonaToolAccessBase, BaseDBMixin):
    pass
