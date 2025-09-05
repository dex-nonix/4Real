from nonix_web.router.web_server_router import router
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .style_schemas import StyleCreate, StyleUpdate, StyleInDbModel
from nonix_web_music_artist.models.style import Style


@router("/styles", tags=["Styles"])
class StyleRouter(NxWebServerCrudRouter):
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
