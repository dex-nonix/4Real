from .persona_mcp_server_schemas import PersonaMCPServerCreate, PersonaMCPServerUpdate, PersonaMCPServerInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import PersonaMCPServer


@routed_service("/persona-mcp-servers", tags=["Persona MCP Servers"])
class PersonaMCPServerService(GenericCRUDService):
    config = CRUDConfig(
        model=PersonaMCPServer,
        create_schema=PersonaMCPServerCreate,
        update_schema=PersonaMCPServerUpdate,
        response_schema=PersonaMCPServerInDB,
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
