from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .persona_mcp_server_schemas import PersonaMCPServerCreate, PersonaMCPServerUpdate, PersonaMCPServerInDbModel
from ...models.persona_mcp_server import PersonaMCPServer


@routed_service("/persona-mcp-servers", tags=["Persona MCP Servers"])
class PersonaMCPServerRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=PersonaMCPServer,
        create_schema=PersonaMCPServerCreate,
        update_schema=PersonaMCPServerUpdate,
        response_schema=PersonaMCPServerInDbModel,
        filters=FilterConfig(
            allowed_fields=['persona_id', 'mcp_server_id', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='id',
            allowed_fields=['id', 'persona_id', 'mcp_server_id', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['persona_id', 'mcp_server_id'],
            display_format='{id}',
            search_fields=[]
        )
    )
