from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from nonix_web_music_artist.services.style_service import StyleService


@router("/styles", tags=["Styles"])
class StyleRouter(NxWebServerCrudRouter):
    service: StyleService = NxInject(StyleService)
