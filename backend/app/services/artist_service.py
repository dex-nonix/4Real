from __future__ import annotations

from .crud_service import CrudService
from ..models.artist import Artist


class ArtistService(CrudService):
    model = Artist
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
            'fields': ['name', 'abbreviation'],
            'display_format': 'name',
            'search_fields': ['name', 'abbreviation']
        },
    }

