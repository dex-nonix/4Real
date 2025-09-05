from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class AlbumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: Optional[date] = None
    artist_id: int = Field(..., gt=0)

    @field_validator('release_date', mode='before')
    @classmethod
    def _normalize_release_date(cls, v):
        if v is None:
            return v
        from nonix_web_db.date_utils import parse_date_strict
        return parse_date_strict(v)


class AlbumCreate(AlbumBase):
    pass


class AlbumUpdate(BaseUpdateModel, base_model=AlbumBase):
    pass


class AlbumInDbModel(AlbumBase, BaseDbModelMixin):
    pass
