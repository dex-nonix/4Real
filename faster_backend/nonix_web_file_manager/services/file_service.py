from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.file.file_schemas import FileCreate, FileUpdate, FileInDbModel
from ..models.file import File


class FileService(BaseCrudService):
    """
    Internal service for file CRUD operations.
    Contains all business logic for file management.
    """
    config = CRUDConfig(
        model=File,
        create_schema=FileCreate,
        update_schema=FileUpdate,
        response_schema=FileInDbModel,
        filters=FilterConfig(
            allowed_fields=['category_id', 'mime_type', 'title', 'original_filename']
        ),
        sorting=SortingConfig(
            default_sort='created_at',
            allowed_fields=['created_at', 'title', 'original_filename', 'size_bytes']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['title', 'original_filename'],
            display_format=None,
            search_fields=['title', 'original_filename', 'mime_type'],
            order_by='created_at'
        )
    )
