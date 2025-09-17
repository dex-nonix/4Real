from typing import Any
from fastapi import UploadFile, Form
from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ...services.file_service import FileService
from ...utils.file_upload_utils import upload_file_logic


@router("/files", tags=["Files"])
class FileRouter(NxWebServerCrudRouter):
    service: FileService = NxInject(FileService)

    @route('/upload', methods=['POST'])
    async def upload(self, file: UploadFile, title: str = Form(None), category_id: int = Form(None)) -> Any:
        return await upload_file_logic(file, title, category_id, self.service)
