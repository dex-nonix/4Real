from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_music_artist.services.album_service import AlbumService


@router("/albums", tags=["Albums"])
class AlbumRouter(NxWebServerCrudRouter):
    service: AlbumService = Inject(AlbumService)
