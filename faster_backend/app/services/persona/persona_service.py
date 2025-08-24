from .persona_schemas import PersonaCreate, PersonaUpdate, PersonaInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import Persona


@routed_service("/personas", tags=["Personas"])
class PersonaService(GenericCRUDService):
    config = CRUDConfig(
        model=Persona,
        create_schema=PersonaCreate,
        update_schema=PersonaUpdate,
        response_schema=PersonaInDB,
        filters=FilterConfig(
            allowed_fields=['name', 'is_active', 'artist_id', 'ai_model_mapping_id']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'artist_id', 'ai_model_mapping_id', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name']
        )
    )
