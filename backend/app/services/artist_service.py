from __future__ import annotations

from .crud_service import CrudService
from ..models.artist import Artist


class ArtistService(CrudService):
    def __init__(self) -> None:
        # Only override defaults where behavior differs
        config = {
            'filters': {
                'fields': ['name', 'abbreviation'],
            },
            'sorting': {
                'default_sort': 'name',
                'allowed_fields': ['name', 'abbreviation', 'created_at'],
            },
            'validation': {
                'required_fields': ['name'],
                'unique_fields': ['name'],
            },
            'selector': {
                'fields': ['id', 'name', 'abbreviation'],
                'display_format': 'name',
                'search_fields': ['name', 'abbreviation']
            },
        }
        super().__init__(Artist, config)
        self.register_routes()

