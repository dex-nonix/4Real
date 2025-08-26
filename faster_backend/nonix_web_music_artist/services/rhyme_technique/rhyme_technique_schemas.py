from pydantic import BaseModel, Field
from nonix_web.services.base_db_model_mixin import BaseDbModelMixin

class RhymeTechniqueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class RhymeTechniqueCreate(RhymeTechniqueBase):
    pass

class RhymeTechniqueUpdate(RhymeTechniqueBase):
    pass

class RhymeTechniqueInDbModel(RhymeTechniqueBase, BaseDbModelMixin):
    pass
