from .persona_tool_access_schemas import PersonaToolAccessCreate, PersonaToolAccessUpdate, PersonaToolAccessInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import PersonaToolAccess


@routed_service("/persona_tool_access", tags=["Persona Tool Access"])
class PersonaToolAccessService(GenericCRUDService):
    config = CRUDConfig(
        model=PersonaToolAccess,
        create_schema=PersonaToolAccessCreate,
        update_schema=PersonaToolAccessUpdate,
        response_schema=PersonaToolAccessInDB,
        filters=FilterConfig(
            allowed_fields=['persona_id', 'pattern', 'allow']
        ),
        sorting=SortingConfig(
            default_sort='id',
            allowed_fields=['id', 'persona_id', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['pattern'],
            display_format='{pattern}',
            search_fields=['pattern']
        )
    )
