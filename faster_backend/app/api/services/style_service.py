from .crud_service import CrudService
from ...models.style import Style


class StyleService(CrudService):
    model = Style
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
