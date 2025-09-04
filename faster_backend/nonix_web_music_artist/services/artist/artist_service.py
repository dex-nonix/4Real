from nonix_web.router.web_server_router import routed_service, route
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .artist_schemas import ArtistCreate, ArtistUpdate, ArtistInDbModel
from ...models.artist import Artist


@routed_service("/artists", tags=["Artists"])
class ArtistService(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=Artist,
        create_schema=ArtistCreate,
        update_schema=ArtistUpdate,
        response_schema=ArtistInDbModel,
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

    ############### EXAMPLE CUSTOM ROUTE ---------------------------
    @route("/{item_id}/persona_summary", methods=["GET"])
    async def persona_summary(self, item_id: int):
        artist = await self.get_one(item_id)
        persona_text = artist.persona or ""
        return {
            "artist_name": artist.name,
            "persona_length": len(persona_text),
            "summary": f"{persona_text[:75]}..." if len(persona_text) > 75 else persona_text
        }
