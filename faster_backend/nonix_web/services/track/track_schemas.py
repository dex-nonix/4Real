from pydantic import BaseModel, Field
from typing import Optional
from ..base_schemas import BaseDBMixin

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

class TrackInDB(TrackBase, BaseDBMixin):
    pass
