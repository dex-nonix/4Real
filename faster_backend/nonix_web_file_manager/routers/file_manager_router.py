from fastapi import Request, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import os

from nonix_di.resolve import NxInject
from nonix_web.router.decorators import router, route
from nonix_web.router.web_server_router import NxWebServerRouter
from nonix_web_db.crud.query_processor import process_query
from .file_manager_schemas import (
    FileUploadResponse, FileDeleteResponse, FileCopyResponse, FileMoveResponse,
    FileRenameResponse, CategoryCreateResponse, CategoryUpdateResponse,
    BulkOperationResponse, FileListResponse, CategoryListResponse, CategoryWithCountListResponse,
    FileManagerFileResponse, FileManagerListResponse
)
from ..services.file_category_service import FileCategoryService
from ..services.file_link_service import FileLinkService
from ..services.file_service import FileService
from ..utils.file_upload_utils import upload_file_logic


@router("/file-manager", tags=["File Manager"])
class FileManagerRouter(NxWebServerRouter):
    """Clean, independent file manager API without CRUD conflicts"""

    file_service: FileService = NxInject(FileService)
    category_service: FileCategoryService = NxInject(FileCategoryService)
    link_service: FileLinkService = NxInject(FileLinkService)

    # File Operations
    @route('/upload', methods=['POST'], response_model=FileUploadResponse)
    async def upload_file(self, file: UploadFile, title: str = Form(None),
                          category_id: int = Form(None)) -> FileUploadResponse:
        """Upload single file with validation"""
        return await upload_file_logic(file, title, category_id, self.file_service)

    @route('/files', methods=['GET'], response_model=FileManagerListResponse)
    async def list_files(self, req: Request) -> FileManagerListResponse:
        base_url = f"{req.url.scheme}://{req.url.netloc}"
        results = await self.file_service.get_all(await process_query(self.file_service, req))
        response_data = [FileManagerFileResponse.from_file_data(item, base_url) for item in results["data"]]
        return FileManagerListResponse(
            data=response_data,
            pagination=results.get("pagination", {})
        )

    @route('/files/{file_id}', methods=['GET'], response_model=FileManagerFileResponse)
    async def get_file_info(self, file_id: int, req: Request) -> FileManagerFileResponse:
        file_data = await self.file_service.get_one(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        base_url = f"{req.url.scheme}://{req.url.netloc}"
        return FileManagerFileResponse.from_file_data(file_data, base_url)

    @route('/files/{id}', methods=['DELETE'], response_model=FileDeleteResponse)
    async def delete_file(self, req: Request, id: int) -> FileDeleteResponse:
        """Delete file by ID"""
        try:
            await self.file_service.delete(item_id=id)
            return FileDeleteResponse(message="File deleted successfully", status="success")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    @route('/files/copy', methods=['POST'], response_model=FileCopyResponse)
    async def copy_files(self, req: Request) -> FileCopyResponse:
        """Copy files to different category"""
        try:
            body = await req.json()
            file_ids = body.get('fileIds', [])
            target_category_id = body.get('targetCategoryId')
            result = await self.file_service.copy_files(file_ids, target_category_id)
            return FileCopyResponse(message=result["message"], count=result["count"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Copy failed: {str(e)}")

    @route('/files/move', methods=['POST'], response_model=FileMoveResponse)
    async def move_files(self, req: Request) -> FileMoveResponse:
        """Move files to different category"""
        try:
            body = await req.json()
            file_ids = body.get('fileIds', [])
            target_category_id = body.get('targetCategoryId')
            result = await self.file_service.move_files(file_ids, target_category_id)
            return FileMoveResponse(message=result["message"], count=result["count"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Move failed: {str(e)}")

    @route('/files/{id}/rename', methods=['PUT'], response_model=FileRenameResponse)
    async def rename_file(self, req: Request, id: int) -> FileRenameResponse:
        """Rename file by ID"""
        try:
            body = await req.json()
            result = await self.file_service.update(item_id=id, data=body)
            return FileRenameResponse(data=result, status="success")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")

    # Category Operations
    @route('/categories', methods=['GET'], response_model=CategoryListResponse)
    async def list_categories(self, req: Request) -> CategoryListResponse:
        """List all categories"""
        return await self.category_service.get_all(await process_query(self.category_service, req))

    @route('/categories', methods=['POST'], response_model=CategoryCreateResponse)
    async def create_category(self, req: Request) -> CategoryCreateResponse:
        """Create new category"""
        try:
            body = await req.json()
            result = await self.category_service.create(data=body)
            return CategoryCreateResponse(data=result, status="success")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Create category failed: {str(e)}")

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
        try:
            body = await req.json()
            result = await self.category_service.update(item_id=id, data=body)
            return CategoryUpdateResponse(data=result, status="success")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update category failed: {str(e)}")

    # Bulk Operations
    @route('/bulk/delete', methods=['POST'], response_model=BulkOperationResponse)
    async def bulk_delete_files(self, req: Request) -> BulkOperationResponse:
        """Bulk delete files"""
        try:
            body = await req.json()
            file_ids = body.get('fileIds', [])
            deleted_count = 0
            for file_id in file_ids:
                await self.file_service.delete(item_id=file_id)
                deleted_count += 1
            return BulkOperationResponse(message="Files deleted successfully", count=deleted_count)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")

    @route('/bulk/copy', methods=['POST'], response_model=BulkOperationResponse)
    async def bulk_copy_files(self, req: Request) -> BulkOperationResponse:
        """Bulk copy files to different category"""
        try:
            body = await req.json()
            file_ids = body.get('fileIds', [])
            target_category_id = body.get('targetCategoryId')
            result = await self.file_service.bulk_copy_files(file_ids, target_category_id)
            return BulkOperationResponse(message=result["message"], count=result["count"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bulk copy failed: {str(e)}")

    @route('/bulk/move', methods=['POST'], response_model=BulkOperationResponse)
    async def bulk_move_files(self, req: Request) -> BulkOperationResponse:
        """Bulk move files to different category"""
        try:
            body = await req.json()
            file_ids = body.get('fileIds', [])
            target_category_id = body.get('targetCategoryId')
            result = await self.file_service.bulk_move_files(file_ids, target_category_id)
            return BulkOperationResponse(message=result["message"], count=result["count"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bulk move failed: {str(e)}")
