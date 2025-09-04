from nonix_web.router.web_server_router import router
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .persona_tool_access_schemas import PersonaToolAccessCreate, PersonaToolAccessUpdate, PersonaToolAccessInDbModel
from ...models.persona_tool_access import PersonaToolAccess


@router("/persona-tool-access", tags=["Persona Tool Access"])
class PersonaToolAccessRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=PersonaToolAccess,
        create_schema=PersonaToolAccessCreate,
        update_schema=PersonaToolAccessUpdate,
        response_schema=PersonaToolAccessInDbModel,
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
