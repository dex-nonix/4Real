from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from nonix_web_agentic.services.internal_tool_service import InternalToolService


@router("/internal-tools", tags=["Internal Tools"])
class InternalToolRouter(NxWebServerCrudRouter):
    service: InternalToolService = NxInject(InternalToolService)
