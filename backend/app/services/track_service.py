from __future__ import annotations

from .crud_service import CrudService
from ..models.track import Track


class TrackService(CrudService):
    def __init__(self) -> None:
        config = {
            'filters': {
                'fields': ['title', 'album_id', 'track_number'],
            },
            'sorting': {
                'default_sort': 'track_number',
                'allowed_fields': ['title', 'track_number', 'created_at'],
            },
            'validation': {
                'required_fields': ['title', 'album_id'],
                'unique_fields': [],
            },
            'selector': {
                'fields': ['title', 'track_number'],
                'display_format': 'title',
                'search_fields': ['title'],
            },
        }
        super().__init__(Track, config)
        self.register_routes()

