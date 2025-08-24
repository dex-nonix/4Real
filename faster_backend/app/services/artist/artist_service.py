from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from .artist_schemas import ArtistCreate, ArtistUpdate, ArtistInDB
from ...crud.generic_crud import GenericCRUDRouter, routed_service, route
from ...crud.models_and_schemas import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig
from ...models import Artist



# Define the service class that inherits from the generic engine
@routed_service(prefix="/artists", tags=["Artists"])
class ArtistService(GenericCRUDRouter):
    # This single config object is the complete 1:1 port of your old system
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

    # Define any custom routes here using the same router instance
    # @artist_router.get("/{item_id}/persona_summary", response_model=dict)
    @route("/{item_id}/persona_summary", methods=["GET"])
    async def persona_summary(self, item_id: int, db: AsyncSession = Depends(get_db)):
        artist = await self.service.get_one(db, item_id)
        persona_text = artist.persona or ""
        return {"artist_name": artist.name, "persona_length": len(persona_text), "summary": f"{persona_text[:75]}..." if len(persona_text) > 75 else persona_text}