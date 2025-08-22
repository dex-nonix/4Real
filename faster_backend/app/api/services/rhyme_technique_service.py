from __future__ import annotations

from .crud_service import CrudService
from ...models.rhyme_technique import RhymeTechnique


class RhymeTechniqueService(CrudService):
    model = RhymeTechnique
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
