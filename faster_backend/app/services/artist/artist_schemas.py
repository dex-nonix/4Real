from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class ArtistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    abbreviation: Optional[str] = Field(None, max_length=50)
    persona: Optional[str] = None
    birth_date: Optional[date] = None

class ArtistCreate(ArtistBase):
    pass

class ArtistUpdate(ArtistBase):
    pass

class ArtistInDB(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)