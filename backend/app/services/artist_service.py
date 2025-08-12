from __future__ import annotations

from .crud_service import CrudService
from ..models.artist import Artist


class ArtistService(CrudService):
    def __init__(self) -> None:
        config = {
            'operations': {
                'create': True,
                'read': True,
                'update': True,
                'delete': True,
                'list': True,
                'search': True,
                'bulk': True,
                'selector': True,
            },
            'filters': {
                'enabled': True,
                'fields': ['name', 'abbreviation'],
                'operators': ['eq', 'ne', 'gt', 'lt', 'like', 'in'],
            },
            'pagination': {
                'enabled': True,
                'default_page_size': 20,
                'max_page_size': 100,
            },
            'sorting': {
                'enabled': True,
                'default_sort': 'name',
                'allowed_fields': ['name', 'abbreviation', 'created_at'],
            },
            'validation': {
                'enabled': True,
                'required_fields': ['name'],
                'unique_fields': ['name'],
            },
            'selector': {
                'enabled': True,
                'fields': ['id', 'name', 'abbreviation'],
                'display_format': 'name',
                'search_fields': ['name', 'abbreviation'],
                'limit': 50,
                'order_by': 'name',
            },
        }
        super().__init__(Artist, config)
        self.register_routes()

