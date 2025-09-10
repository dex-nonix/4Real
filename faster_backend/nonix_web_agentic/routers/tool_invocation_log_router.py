from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.tool_invocation_log_service import ToolInvocationLogService


@router("/tool-invocation-logs", tags=["Tool Invocation Logs"])
class ToolInvocationLogRouter(NxWebServerCrudRouter):
    service: ToolInvocationLogService = NxInject(ToolInvocationLogService)
