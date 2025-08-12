from __future__ import annotations

from .crud_service import CrudService
from ..models.ai_model_mapping import AIModelMapping


class AIModelMappingService(CrudService):
    def __init__(self) -> None:
        config = {
            'filters': {
                'fields': ['provider_id', 'purpose', 'model_name', 'is_active'],
            },
            'sorting': {
                'default_sort': 'purpose',
                'allowed_fields': ['purpose', 'model_name', 'created_at'],
            },
            'validation': {
                'required_fields': ['provider_id', 'purpose', 'model_name'],
                'unique_fields': [],
            },
            'selector': {
                'fields': ['purpose', 'model_name'],
                'display_format': 'purpose',
                'search_fields': ['purpose', 'model_name'],
            },
        }
        super().__init__(AIModelMapping, config)

