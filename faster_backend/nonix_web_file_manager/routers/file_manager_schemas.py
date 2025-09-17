from pydantic import BaseModel
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
