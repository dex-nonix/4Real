from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .style_schemas import StyleCreate, StyleUpdate, StyleInDbModel
from ...models.style import Style


@routed_service("/styles", tags=["Styles"])
class StyleService(GenericCRUDService):
    config = CRUDConfig(
        model=Style,
        create_schema=StyleCreate,
        update_schema=StyleUpdate,
        response_schema=StyleInDbModel,
        filters=FilterConfig(
            allowed_fields=['name']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at']
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
