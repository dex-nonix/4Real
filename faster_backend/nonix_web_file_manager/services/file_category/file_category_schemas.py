from pydantic import BaseModel, Field
from typing import Optional
from nonix_web.services.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel

class FileCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class FileCategoryCreate(FileCategoryBase):
    pass

class FileCategoryUpdate(BaseUpdateModel, base_model=FileCategoryBase):
    pass

class FileCategoryInDbModel(FileCategoryBase, BaseDbModelMixin):
    pass
