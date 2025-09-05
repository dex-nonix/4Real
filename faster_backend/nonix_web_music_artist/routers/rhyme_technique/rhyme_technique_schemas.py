from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class RhymeTechniqueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class RhymeTechniqueCreate(RhymeTechniqueBase):
    pass


class RhymeTechniqueUpdate(BaseUpdateModel, base_model=RhymeTechniqueBase):
    pass


class RhymeTechniqueInDbModel(RhymeTechniqueBase, BaseDbModelMixin):
    pass
