from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ...services.album_service import AlbumService


@router("/albums", tags=["Albums"])
class AlbumRouter(NxWebServerCrudRouter):
    service: AlbumService = NxInject(AlbumService)
