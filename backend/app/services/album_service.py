from __future__ import annotations

from .crud_service import CrudService
from ..models.album import Album


class AlbumService(CrudService):
    model = Album
    config = {
        'filters': {
            'fields': ['title', 'release_date', 'artist_id'],
        },
        'sorting': {
            'default_sort': 'release_date',
            'allowed_fields': ['title', 'release_date', 'created_at'],
        },
        'validation': {
            'required_fields': ['title', 'artist_id'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['title', 'release_date'],
            'display_format': 'title',
            'search_fields': ['title'],
        },
    }

