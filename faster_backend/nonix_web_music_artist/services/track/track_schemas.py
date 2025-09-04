from typing import Optional

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class TrackBase(BaseModel):
    album_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    track_number: Optional[int] = Field(None, ge=1)
    duration_seconds: Optional[int] = Field(None, ge=0)
    lyrics: Optional[str] = None


class TrackCreate(TrackBase):
    pass


class TrackUpdate(BaseUpdateModel, base_model=TrackBase):
    pass


class TrackInDbModel(TrackBase, BaseDbModelMixin):
    pass
