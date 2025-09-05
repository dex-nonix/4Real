from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_agentic.services.persona_mcp_server_service import PersonaMCPServerService


@router("/persona-mcp-servers", tags=["Persona MCP Servers"])
class PersonaMCPServerRouter(NxWebServerCrudRouter):
    service: PersonaMCPServerService = Inject(PersonaMCPServerService)
