from dataclasses import field
from typing import Optional

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel



class RhymeTechniqueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class RhymeTechniqueCreate(RhymeTechniqueBase):
    pass


class RhymeTechniqueUpdate(BaseUpdateModel, base_model=RhymeTechniqueBase): #does  not work
    pass

class Working_RhymeTechniqueUpdate(BaseModel): # does work
    name: Optional[str] = Field(..., min_length=1, max_length=255)


class RhymeTechniqueInDbModel(RhymeTechniqueBase, BaseDbModelMixin):
    pass
