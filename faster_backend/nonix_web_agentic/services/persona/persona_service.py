from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService

from nonix_web.services.base_service import routed_service
from .persona_schemas import PersonaCreate, PersonaUpdate, PersonaInDbModel
from ...models.persona import Persona


@routed_service("/personas", tags=["Personas"])
class PersonaService(GenericCRUDService):
    config = CRUDConfig(
        model=Persona,
        create_schema=PersonaCreate,
        update_schema=PersonaUpdate,
        response_schema=PersonaInDbModel,
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
