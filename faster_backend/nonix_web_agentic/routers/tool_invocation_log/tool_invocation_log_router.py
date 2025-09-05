from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.tool_invocation_log_service import ToolInvocationLogService


@router("/tool-invocation-logs", tags=["Tool Invocation Logs"])
class ToolInvocationLogRouter(NxWebServerCrudRouter):
    service: ToolInvocationLogService = Inject(ToolInvocationLogService)
