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

    async def copy_files(self, file_ids: list, target_category_id: int):
        """Copy files to different category"""
        copied_count = 0
        for file_id in file_ids:
            file_data = await self.get_one(file_id)
            if file_data:
                copy_data = {
                    'category_id': target_category_id,
                    'title': file_data.title,
                    'original_filename': file_data.original_filename,
                    'mime_type': file_data.mime_type,
                    'size_bytes': file_data.size_bytes,
                    'storage_url': file_data.storage_url,
                    'sha256': file_data.sha256
                }
                await self.create(copy_data)
                copied_count += 1
        return {"message": "Files copied successfully", "count": copied_count}

    async def move_files(self, file_ids: list, target_category_id: int):
        """Move files to different category"""
        moved_count = 0
        for file_id in file_ids:
            update_data = {'category_id': target_category_id}
            await self.update(file_id, update_data)
            moved_count += 1
        return {"message": "Files moved successfully", "count": moved_count}

    async def bulk_copy_files(self, file_ids: list, target_category_id: int):
        """Bulk copy files to different category"""
        return await self.copy_files(file_ids, target_category_id)

    async def bulk_move_files(self, file_ids: list, target_category_id: int):
        """Bulk move files to different category"""
        return await self.move_files(file_ids, target_category_id)


