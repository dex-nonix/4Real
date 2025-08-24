from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from ..base_schemas import BaseDBMixin

class AlbumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: Optional[date] = None
    artist_id: int = Field(..., gt=0)

class AlbumCreate(AlbumBase):
    pass

class AlbumUpdate(AlbumBase):
    pass

class AlbumInDB(AlbumBase, BaseDBMixin):
    pass
