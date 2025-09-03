from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class PersonaToolAccessBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    pattern: str = Field(..., min_length=1, max_length=255)
    allow: bool = True


class PersonaToolAccessCreate(PersonaToolAccessBase):
    pass


class PersonaToolAccessUpdate(BaseUpdateModel, base_model=PersonaToolAccessBase):
    pass


class PersonaToolAccessInDbModel(PersonaToolAccessBase, BaseDbModelMixin):
    pass
