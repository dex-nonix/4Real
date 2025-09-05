from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.style.style_schemas import StyleCreate, StyleUpdate, StyleInDbModel
from ..models.style import Style


class StyleService(BaseCrudService):
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
