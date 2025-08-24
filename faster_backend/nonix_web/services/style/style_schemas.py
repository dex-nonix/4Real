from pydantic import BaseModel, Field
from ..base_schemas import BaseDBMixin

class StyleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class StyleCreate(StyleBase):
    pass

class StyleUpdate(StyleBase):
    pass

class StyleInDB(StyleBase, BaseDBMixin):
    pass
