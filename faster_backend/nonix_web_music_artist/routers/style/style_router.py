from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ...services.style_service import StyleService


@router("/styles", tags=["Styles"])
class StyleRouter(NxWebServerCrudRouter):
    service: StyleService = NxInject(StyleService)
