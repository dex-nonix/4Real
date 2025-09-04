from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .file_link_schemas import FileLinkCreate, FileLinkUpdate, FileLinkInDbModel
from ...models.file_link import FileLink


@routed_service("/file-links", tags=["File Links"])
class FileLinkService(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=FileLink,
        create_schema=FileLinkCreate,
        update_schema=FileLinkUpdate,
        response_schema=FileLinkInDbModel,
        filters=FilterConfig(
            allowed_fields=['entity_type', 'entity_id', 'status', 'file_id']
        ),
        sorting=SortingConfig(
            default_sort='sort_order',
            allowed_fields=['sort_order', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=[],
            display_format=None,
            search_fields=[],
            order_by='created_at'
        )
    )
