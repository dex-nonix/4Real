from .mcp_server_schemas import MCPServerCreate, MCPServerUpdate, MCPServerInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import MCPServer


@routed_service("/mcp-servers", tags=["MCP Servers"])
class MCPServerService(GenericCRUDService):
    config = CRUDConfig(
        model=MCPServer,
        create_schema=MCPServerCreate,
        update_schema=MCPServerUpdate,
        response_schema=MCPServerInDB,
        filters=FilterConfig(
            allowed_fields=['name', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name']
        )
    )
