from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from nonix_web_music_artist.services.album_service import AlbumService


@router("/albums", tags=["Albums"])
class AlbumRouter(NxWebServerCrudRouter):
    service: AlbumService = NxInject(AlbumService)
