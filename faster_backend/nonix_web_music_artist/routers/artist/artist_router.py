from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from ...services.artist_service import ArtistService


@router("/artists", tags=["Artists"])
class ArtistRouter(NxWebServerCrudRouter):
    service: ArtistService = NxInject(ArtistService)

    ############### EXAMPLE CUSTOM ROUTE ---------------------------
    @route("/{item_id}/persona_summary", methods=["GET"])
    async def persona_summary(self, item_id: int):
        artist = await self.service.get_one(item_id)
        persona_text = artist.persona or ""
        return {
            "artist_name": artist.name,
            "persona_length": len(persona_text),
            "summary": f"{persona_text[:75]}..." if len(persona_text) > 75 else persona_text
        }
