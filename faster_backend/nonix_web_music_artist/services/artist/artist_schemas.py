from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from nonix_web.services.base_db_model_mixin import BaseDbModelMixin

class ArtistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    abbreviation: Optional[str] = Field(None, max_length=50)
    persona: Optional[str] = None
    birth_date: Optional[date] = None

class ArtistCreate(ArtistBase):
    pass

class ArtistUpdate(ArtistBase):
    pass

class ArtistInDbModel(ArtistBase, BaseDbModelMixin):
    pass