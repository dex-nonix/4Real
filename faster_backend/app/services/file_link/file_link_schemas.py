from pydantic import BaseModel, Field
from typing import Optional
from ..base_schemas import BaseDBMixin

class FileLinkBase(BaseModel):
    file_id: int = Field(..., gt=0)
    entity_type: str = Field(..., min_length=1, max_length=64)
    entity_id: int = Field(..., gt=0)
    status: str = Field(..., min_length=1, max_length=32)
    comment: Optional[str] = None
    sort_order: int = Field(default=0)

class FileLinkCreate(FileLinkBase):
    pass

class FileLinkUpdate(FileLinkBase):
    pass

class FileLinkInDB(FileLinkBase, BaseDBMixin):
    pass
