from __future__ import annotations

from .crud_service import CrudService
from ..models.style import Style


class StyleService(CrudService):
    def __init__(self) -> None:
        config = {
            'filters': {
                'fields': ['name'],
            },
            'sorting': {
                'default_sort': 'name',
                'allowed_fields': ['name', 'created_at'],
            },
            'validation': {
                'required_fields': ['name'],
                'unique_fields': ['name'],
            },
            'selector': {
                'fields': ['name'],
                'display_format': 'name',
                'search_fields': ['name'],
            },
        }
        super().__init__(Style, config)
        self.register_routes()

