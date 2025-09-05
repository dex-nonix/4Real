from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ..services.template_service import TemplateService


@router("/templates", tags=["Templates"])
class TemplateRouter(NxWebServerCrudRouter):
    service: TemplateService = Inject(TemplateService)  # ✅ Just inject!
