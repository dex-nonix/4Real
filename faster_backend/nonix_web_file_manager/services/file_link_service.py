from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.file_link.file_link_router import FileLinkCreate, FileLinkUpdate, FileLinkInDbModel
from ..models.file_link import FileLink


class FileLinkService(BaseCrudService):
    """
    Internal service for file link CRUD operations.
    Contains all business logic for file link management.
    """
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
