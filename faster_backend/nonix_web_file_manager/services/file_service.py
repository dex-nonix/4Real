from typing import Dict, Any

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.file.file_schemas import FileCreate, FileUpdate, FileInDbModel
from ..models.file import File


class FileService(BaseCrudService):
    max_file_size = None
    allowed_extensions = None
    upload_folder = None
    sha256_required = None
    auto_create_dirs = None

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
    def __init__(self):
        super().__init__()
        self.max_file_size = None
        self.allowed_extensions = None
        self.upload_folder = None
        self.sha256_required = None
        self.auto_create_dirs = None

    async def initialize(self, config: Dict[str, Any]):
        self.max_file_size = config["max_file_size"]
        self.allowed_extensions = config["allowed_extensions"]
        self.upload_folder = config["upload_folder"]
        self.sha256_required = config["sha256_required"]
        self.auto_create_dirs = config["auto_create_dirs"]


