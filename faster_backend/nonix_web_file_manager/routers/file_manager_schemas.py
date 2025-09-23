import os
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from nonix_web_db.crud.models_and_schemas import PaginatedResponse
from .file.file_schemas import FileInDbModel
from .file_category.file_category_schemas import FileCategoryInDbModel, FileCategoryWithCountModel


class FileUploadResponse(BaseModel):
    data: FileInDbModel
    status: str = "success"


class FileDeleteResponse(BaseModel):
    message: str = "File deleted successfully"
    status: str = "success"


class FileCopyResponse(BaseModel):
    message: str = "Files copied successfully"
    status: str = "success"
    count: int


class FileMoveResponse(BaseModel):
    message: str = "Files moved successfully"
    status: str = "success"
    count: int


class FileRenameResponse(BaseModel):
    data: FileInDbModel
    status: str = "success"


class CategoryCreateResponse(BaseModel):
    data: FileCategoryInDbModel
    status: str = "success"


class CategoryUpdateResponse(BaseModel):
    data: FileCategoryInDbModel
    status: str = "success"


class BulkOperationResponse(BaseModel):
    message: str
    status: str = "success"
    count: int


# Paginated responses
FileListResponse = PaginatedResponse[FileInDbModel]
CategoryListResponse = PaginatedResponse[FileCategoryInDbModel]
CategoryWithCountListResponse = PaginatedResponse[FileCategoryWithCountModel]


class FileManagerFileResponse(BaseModel):
    id: int
    category_id: Optional[int] = None
    title: Optional[str] = None
    original_filename: str
    mime_type: str
    size_bytes: int
    url: str
    sha256: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None

    @classmethod
    def from_file_data(cls, file_data, base_url: str):
        if file_data.storage_url.startswith(('http://', 'https://')):
            computed_url = file_data.storage_url
        else:
            computed_url = f"{base_url}{file_data.storage_url}"

        return cls(
            id=file_data.id,
            category_id=file_data.category_id,
            title=file_data.title,
            original_filename=file_data.original_filename,
            mime_type=file_data.mime_type,
            size_bytes=file_data.size_bytes,
            url=computed_url,
            sha256=file_data.sha256,
            width=file_data.width,
            height=file_data.height,
            duration_seconds=file_data.duration_seconds
        )


class FileManagerListResponse(BaseModel):
    data: List[FileManagerFileResponse]
    pagination: Dict[str, Any]
