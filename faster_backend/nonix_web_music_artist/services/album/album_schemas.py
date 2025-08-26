from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


class AlbumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: Optional[date] = None
    artist_id: int = Field(..., gt=0)


class AlbumCreate(AlbumBase):
    pass


class AlbumUpdate(AlbumBase):
    pass


class AlbumInDbModel(AlbumBase, BaseDbModelMixin):
    pass
