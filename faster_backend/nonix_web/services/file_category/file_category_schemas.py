from pydantic import BaseModel, Field
from typing import Optional
from ..base_schemas import BaseDBMixin

class FileCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class FileCategoryCreate(FileCategoryBase):
    pass

class FileCategoryUpdate(FileCategoryBase):
    pass

class FileCategoryInDB(FileCategoryBase, BaseDBMixin):
    pass
