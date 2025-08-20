from __future__ import annotations

from .crud_service import CrudService
from ..models.ai_provider import AIProvider


class AIProviderService(CrudService):
    model = AIProvider
    config = {
        'filters': {
            'fields': ['name', 'provider_type', 'module', 'cls', 'method', 'is_active'],
        },
        'sorting': {
            'default_sort': 'name',
            'allowed_fields': ['name', 'provider_type', 'module', 'cls', 'method', 'created_at'],
        },
        'validation': {
            'required_fields': ['name', 'provider_type', 'module', 'cls'],
            'unique_fields': ['name'],
        },
        'selector': {
            'fields': ['name', 'provider_type', 'module', 'cls', 'method'],
            'display_format': 'name',
            'search_fields': ['name', 'provider_type', 'module', 'cls'],
        },
    }
