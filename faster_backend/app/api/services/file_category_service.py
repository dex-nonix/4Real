from .crud_service import CrudService
from ...models.file_category import FileCategory


class FileCategoryService(CrudService):
    model = FileCategory
    config = {
        'filters': {
            'fields': ['name', 'slug'],
        },
        'sorting': {
            'default_sort': 'name',
            'allowed_fields': ['name', 'created_at'],
        },
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['slug'],
        },
        'selector': {
            'fields': ['name'],
            'display_format': 'name',
            'search_fields': ['name', 'slug'],
            'order_by': 'name',
        },
    }
