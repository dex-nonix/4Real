from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.di import Inject
from nonix_web_agentic.services.mcp_server_service import MCPServerService


@router("/mcp-servers", tags=["MCP Servers"])
class MCPServerRouter(NxWebServerCrudRouter):
    service: MCPServerService = Inject(MCPServerService)
