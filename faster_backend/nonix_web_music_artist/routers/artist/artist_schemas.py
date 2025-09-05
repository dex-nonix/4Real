from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class ArtistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    abbreviation: Optional[str] = Field(None, max_length=50)
    persona: Optional[str] = None
    birth_date: Optional[date] = None


class ArtistCreate(ArtistBase):
    pass


class ArtistUpdate(BaseUpdateModel, base_model=ArtistBase):
    pass


class ArtistInDbModel(ArtistBase, BaseDbModelMixin):
    pass
