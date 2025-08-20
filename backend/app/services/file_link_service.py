from __future__ import annotations

from .crud_service import CrudService
from ..models.file_link import FileLink


class FileLinkService(CrudService):
    model = FileLink
    config = {
        'filters': {
            'fields': ['entity_type', 'entity_id', 'status', 'file_id'],
        },
        'sorting': {
            'default_sort': 'sort_order',
            'allowed_fields': ['sort_order', 'created_at'],
        },
        'validation': {
            'required_fields': ['file_id', 'entity_type', 'entity_id', 'status'],
            'unique_fields': [],
        },
        'selector': {
            'fields': [],
            'display_format': None,
            'search_fields': [],
            'order_by': 'created_at',
        },
    }
