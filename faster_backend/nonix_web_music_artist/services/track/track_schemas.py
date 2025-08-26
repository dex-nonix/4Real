from pydantic import BaseModel, Field
from typing import Optional
from nonix_web.services.base_db_model_mixin import BaseDbModelMixin

class TrackBase(BaseModel):
    album_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    track_number: Optional[int] = Field(None, ge=1)
    duration_seconds: Optional[int] = Field(None, ge=0)
    lyrics: Optional[str] = None

class TrackCreate(TrackBase):
    pass

class TrackUpdate(TrackBase):
    pass

class TrackInDbModel(TrackBase, BaseDbModelMixin):
    pass
