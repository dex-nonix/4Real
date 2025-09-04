from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class StyleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class StyleCreate(StyleBase):
    pass


class StyleUpdate(BaseUpdateModel, base_model=StyleBase):
    pass


class StyleInDbModel(StyleBase, BaseDbModelMixin):
    pass
