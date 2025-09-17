from fastapi import Request, UploadFile, Form
from nonix_web.router.decorators import router, route
from nonix_di.resolve import NxInject
from nonix_web.router.web_server_router import NxWebServerRouter
from nonix_web_db.crud.query_processor import QueryProcessor
from ..services.file_service import FileService
from ..services.file_category_service import FileCategoryService
from ..services.file_link_service import FileLinkService
from ..utils.file_upload_utils import upload_file_logic
from .file_manager_schemas import (
    FileUploadResponse, FileDeleteResponse, FileCopyResponse, FileMoveResponse,
    FileRenameResponse, CategoryCreateResponse, CategoryUpdateResponse,
    BulkOperationResponse, FileListResponse, CategoryListResponse, CategoryWithCountListResponse
)


@router("/file-manager", tags=["File Manager"])
class FileManagerRouter(NxWebServerRouter):
    """Clean, independent file manager API without CRUD conflicts"""
    
    file_service: FileService = NxInject(FileService)
    category_service: FileCategoryService = NxInject(FileCategoryService)
    link_service: FileLinkService = NxInject(FileLinkService)
    
    # File Operations
    @route('/upload', methods=['POST'], response_model=FileUploadResponse)
    async def upload_file(self, file: UploadFile, title: str = Form(None), category_id: int = Form(None)) -> FileUploadResponse:
        """Upload single file with validation"""
        return await upload_file_logic(file, title, category_id, self.file_service)
    
    @route('/files', methods=['GET'], response_model=FileListResponse)
    async def list_files(self, req: Request) -> FileListResponse:
        """List files with category information"""
        query_processor = QueryProcessor(model=self.file_service.model, config=self.file_service.config)
        q_params = await query_processor(req)
        return await self.file_service.get_all(q_params)
    
    @route('/files/{id}', methods=['DELETE'], response_model=FileDeleteResponse)
    async def delete_file(self, req: Request, id: int) -> FileDeleteResponse:
        """Delete file by ID"""
        return await self.service_call_and_respond(
            self.file_service.delete, (), {'item_id': id}
        )
    
    @route('/files/copy', methods=['POST'], response_model=FileCopyResponse)
    async def copy_files(self, req: Request) -> FileCopyResponse:
        """Copy files to different category"""
        body = await req.json()
        file_ids = body.get('fileIds', [])
        target_category_id = body.get('targetCategoryId')
        result = await self.file_service.copy_files(file_ids, target_category_id)
        return FileCopyResponse(message=result["message"], count=result["count"])
    
    @route('/files/move', methods=['POST'], response_model=FileMoveResponse)
    async def move_files(self, req: Request) -> FileMoveResponse:
        """Move files to different category"""
        body = await req.json()
        file_ids = body.get('fileIds', [])
        target_category_id = body.get('targetCategoryId')
        result = await self.file_service.move_files(file_ids, target_category_id)
        return FileMoveResponse(message=result["message"], count=result["count"])
    
    @route('/files/{id}/rename', methods=['PUT'], response_model=FileRenameResponse)
    async def rename_file(self, req: Request, id: int) -> FileRenameResponse:
        """Rename file by ID"""
        body = await req.json()
        return await self.service_call_and_respond(
            self.file_service.update, (), {'item_id': id, 'data': body}
        )
    
    # Category Operations
    @route('/categories', methods=['GET'], response_model=CategoryListResponse)
    async def list_categories(self, req: Request) -> CategoryListResponse:
        """List all categories"""
        query_processor = QueryProcessor(model=self.category_service.model, config=self.category_service.config)
        q_params = await query_processor(req)
        return await self.category_service.get_all(q_params)
    
    @route('/categories', methods=['POST'], response_model=CategoryCreateResponse)
    async def create_category(self, req: Request) -> CategoryCreateResponse:
        """Create new category"""
        body = await req.json()
        return await self.service_call_and_respond(
            self.category_service.create, (), {'data': body}
        )
    
    @route('/categories/with-counts', methods=['GET'], response_model=CategoryWithCountListResponse)
    async def get_categories_with_counts(self, req: Request) -> CategoryWithCountListResponse:
        """Get categories with file counts"""
        result = await self.category_service.get_categories_with_file_counts()
        from nonix_web_db.crud.models_and_schemas import PaginationInfo
        pagination = PaginationInfo(
            page=1,
            per_page=len(result["data"]),
            total=result["total"],
            pages=1,
            has_next=False,
            has_prev=False
        )
        return CategoryWithCountListResponse(data=result["data"], pagination=pagination)
    
    @route('/categories/{id}', methods=['PUT'], response_model=CategoryUpdateResponse)
    async def update_category(self, req: Request, id: int) -> CategoryUpdateResponse:
        """Update category by ID"""
        body = await req.json()
        return await self.service_call_and_respond(
            self.category_service.update, (), {'item_id': id, 'data': body}
        )
    
    # Bulk Operations
    @route('/bulk/copy', methods=['POST'], response_model=BulkOperationResponse)
    async def bulk_copy_files(self, req: Request) -> BulkOperationResponse:
        """Bulk copy files to different category"""
        body = await req.json()
        file_ids = body.get('fileIds', [])
        target_category_id = body.get('targetCategoryId')
        result = await self.file_service.bulk_copy_files(file_ids, target_category_id)
        return BulkOperationResponse(message=result["message"], count=result["count"])
    
    @route('/bulk/move', methods=['POST'], response_model=BulkOperationResponse)
    async def bulk_move_files(self, req: Request) -> BulkOperationResponse:
        """Bulk move files to different category"""
        body = await req.json()
        file_ids = body.get('fileIds', [])
        target_category_id = body.get('targetCategoryId')
        result = await self.file_service.bulk_move_files(file_ids, target_category_id)
        return BulkOperationResponse(message=result["message"], count=result["count"])
