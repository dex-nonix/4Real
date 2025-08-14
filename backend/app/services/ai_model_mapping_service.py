from __future__ import annotations

from .crud_service import CrudService
from ..models.ai_model_mapping import AIModelMapping


class AIModelMappingService(CrudService):
    def __init__(self) -> None:
        config = {
            'filters': {
                'fields': ['provider_id', 'name', 'model_name', 'is_active'],
            },
            'sorting': {
                'default_sort': 'name',
                'allowed_fields': ['name', 'model_name', 'created_at'],
            },
            'validation': {
                'required_fields': ['provider_id', 'name', 'model_name'],
                'unique_fields': [],
            },
            'selector': {
                'fields': ['name', 'model_name'],
                'display_format': 'name',
                'search_fields': ['name', 'model_name'],
            },
        }
        super().__init__(AIModelMapping, config)

