from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.mcp_server.mcp_server_schemas import MCPServerCreate, MCPServerUpdate, MCPServerInDbModel
from ..models.mcp_server import MCPServer


class MCPServerService(BaseCrudService):
    config = CRUDConfig(
        model=MCPServer,
        create_schema=MCPServerCreate,
        update_schema=MCPServerUpdate,
        response_schema=MCPServerInDbModel,
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
