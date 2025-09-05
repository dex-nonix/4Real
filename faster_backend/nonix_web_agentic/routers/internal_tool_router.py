from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_agentic.services.internal_tool_service import InternalToolService


@router("/internal-tools", tags=["Internal Tools"])
class InternalToolRouter(NxWebServerCrudRouter):
    service: InternalToolService = Inject(InternalToolService)
