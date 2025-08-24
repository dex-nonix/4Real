from pydantic import BaseModel, Field
from ..base_schemas import BaseDBMixin

class RhymeTechniqueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class RhymeTechniqueCreate(RhymeTechniqueBase):
    pass

class RhymeTechniqueUpdate(RhymeTechniqueBase):
    pass

class RhymeTechniqueInDB(RhymeTechniqueBase, BaseDBMixin):
    pass
