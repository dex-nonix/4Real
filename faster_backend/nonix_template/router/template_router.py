from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.template_service import TemplateService


@router("/templates", tags=["Templates"])
class TemplateRouter(NxWebServerCrudRouter):
    service: TemplateService = NxInject(TemplateService)  # ✅ Just inject!
