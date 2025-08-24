from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from .artist_schemas import ArtistCreate, ArtistUpdate, ArtistInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import Artist


@routed_service(prefix="/artists", tags=["Artists"])
class ArtistService(GenericCRUDService):
    config = CRUDConfig(
        model=Artist,
        create_schema=ArtistCreate,
        update_schema=ArtistUpdate,
        response_schema=ArtistInDB,
        filters=FilterConfig(
            allowed_fields=['name', 'abbreviation']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'abbreviation', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name', 'abbreviation'],
            display_format='{name}',
            search_fields=['name', 'abbreviation']
        )
    )

    @route("/{item_id}/persona_summary", methods=["GET"])
    async def persona_summary(self, item_id: int, db: AsyncSession = Depends(get_db)):
        artist = await self.service.get_one(db, item_id)
        persona_text = artist.persona or ""
        return {"artist_name": artist.name, "persona_length": len(persona_text),
                "summary": f"{persona_text[:75]}..." if len(persona_text) > 75 else persona_text}
