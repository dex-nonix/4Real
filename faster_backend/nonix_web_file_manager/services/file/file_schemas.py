from pydantic import BaseModel, Field
from typing import Optional
from nonix_web.services.base_db_model_mixin import BaseDbModelMixin

class FileBase(BaseModel):
    category_id: Optional[int] = Field(None, gt=0)
    title: Optional[str] = Field(None, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=512)
    mime_type: str = Field(..., min_length=1, max_length=255)
    size_bytes: int = Field(..., gt=0)
    storage_url: str = Field(..., min_length=1, max_length=1024)
    sha256: Optional[str] = Field(None, max_length=64)
    width: Optional[int] = Field(None, gt=0)
    height: Optional[int] = Field(None, gt=0)
    duration_seconds: Optional[int] = Field(None, gt=0)

class FileCreate(FileBase):
    pass

class FileUpdate(FileBase):
    pass

class FileInDbModel(FileBase, BaseDbModelMixin):
    pass
