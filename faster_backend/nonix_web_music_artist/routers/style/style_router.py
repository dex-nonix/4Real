from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_music_artist.services.style_service import StyleService


@router("/styles", tags=["Styles"])
class StyleRouter(NxWebServerCrudRouter):
    service: StyleService = Inject(StyleService)
