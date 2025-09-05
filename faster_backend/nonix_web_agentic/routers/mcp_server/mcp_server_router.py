from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.mcp_server_service import MCPServerService


@router("/mcp-servers", tags=["MCP Servers"])
class MCPServerRouter(NxWebServerCrudRouter):
    service: MCPServerService = Inject(MCPServerService)
