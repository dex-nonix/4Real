from __future__ import annotations

from .crud_service import CrudService
from ..models.persona_tool_access import PersonaToolAccess


class PersonaToolAccessService(CrudService):
    model = PersonaToolAccess
    config = {
        'filters': {
            'fields': ['persona_id', 'pattern', 'allow'],
        },
        'sorting': {
            'default_sort': 'id',
            'allowed_fields': ['id', 'persona_id', 'created_at'],
        },
        'validation': {
            'required_fields': ['persona_id', 'pattern'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['pattern'],
            'display_format': 'pattern',
            'search_fields': ['pattern'],
        },
    }


