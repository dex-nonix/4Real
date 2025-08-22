from __future__ import annotations

from .crud_service import CrudService
from ...models.internal_tool import InternalTool


class InternalToolService(CrudService):
    model = InternalTool
    config = {
        'filters': {
            'fields': ['namespace', 'name', 'qualified_name', 'is_active'],
        },
        'sorting': {
            'default_sort': 'qualified_name',
            'allowed_fields': ['namespace', 'name', 'qualified_name', 'created_at'],
        },
        'validation': {
            'required_fields': ['namespace', 'name', 'qualified_name'],
            'unique_fields': ['qualified_name'],
        },
        'selector': {
            'fields': ['qualified_name', 'name', 'namespace'],
            'display_format': 'qualified_name',
            'search_fields': ['qualified_name', 'name', 'namespace'],
        },
    }
