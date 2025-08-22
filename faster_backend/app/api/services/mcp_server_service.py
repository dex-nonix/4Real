from __future__ import annotations

from .crud_service import CrudService
from ...models.mcp_server import MCPServer


class MCPServerService(CrudService):
    model = MCPServer
    config = {
        'filters': {
            'fields': ['name', 'is_active'],
        },
        'sorting': {
            'default_sort': 'name',
            'allowed_fields': ['name', 'created_at'],
        },
        'validation': {
            'required_fields': ['name', 'command'],
            'unique_fields': ['name'],
        },
        'selector': {
            'fields': ['name'],
            'display_format': 'name',
            'search_fields': ['name'],
        },
    }
