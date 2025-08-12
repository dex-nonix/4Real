from __future__ import annotations

from .crud_service import CrudService
from ..models.ai_provider import AIProvider


class AIProviderService(CrudService):
    def __init__(self) -> None:
        config = {
            'filters': {
                'fields': ['name', 'provider_type', 'is_active'],
            },
            'sorting': {
                'default_sort': 'name',
                'allowed_fields': ['name', 'provider_type', 'created_at'],
            },
            'validation': {
                'required_fields': ['name', 'provider_type'],
                'unique_fields': ['name'],
            },
            'selector': {
                'fields': ['name', 'provider_type'],
                'display_format': 'name',
                'search_fields': ['name'],
            },
        }
        super().__init__(AIProvider, config)
        self.register_routes()

