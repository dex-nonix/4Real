from .crud_service import CrudService
from ...models.persona import Persona


class PersonaService(CrudService):
    model = Persona
    config = {
        'filters': {
            'fields': ['name', 'is_active', 'artist_id', 'ai_model_mapping_id'],
        },
        'sorting': {
            'default_sort': 'name',
            'allowed_fields': ['name', 'artist_id', 'ai_model_mapping_id', 'created_at'],
        },
        'validation': {
            'required_fields': ['name', 'ai_model_mapping_id'],
            'unique_fields': ['name'],
        },
        'selector': {
            'fields': ['name'],
            'display_format': 'name',
            'search_fields': ['name'],
        },
    }
