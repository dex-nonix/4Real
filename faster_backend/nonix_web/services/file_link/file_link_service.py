from .file_link_schemas import FileLinkCreate, FileLinkUpdate, FileLinkInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import FileLink


@routed_service("/file_links", tags=["File Links"])
class FileLinkService(GenericCRUDService):
    config = CRUDConfig(
        model=FileLink,
        create_schema=FileLinkCreate,
        update_schema=FileLinkUpdate,
        response_schema=FileLinkInDB,
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
