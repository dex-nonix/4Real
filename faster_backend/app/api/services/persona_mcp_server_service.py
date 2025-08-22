from .crud_service import CrudService
from ...models.persona_mcp_server import PersonaMCPServer


class PersonaMCPServerService(CrudService):
    model = PersonaMCPServer
    config = {
        'filters': {
            'fields': ['persona_id', 'mcp_server_id', 'is_active'],
        },
        'sorting': {
            'default_sort': 'id',
            'allowed_fields': ['id', 'persona_id', 'mcp_server_id', 'created_at'],
        },
        'validation': {
            'required_fields': ['persona_id', 'mcp_server_id'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['persona_id', 'mcp_server_id'],
            'display_format': 'id',
            'search_fields': [],
        },
    }
