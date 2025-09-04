import hashlib
import os
from typing import Any

from fastapi import HTTPException, UploadFile, Form


from nonix_web.router.web_server_router import routed_service, route
from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .file_schemas import FileCreate, FileUpdate, FileInDbModel
from ...models.file import File


@routed_service("/files", tags=["Files"])
class FileService(NxWebServerCrudRouter):
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

    @route('/upload', methods=['POST'])
    async def upload(self, file: UploadFile, title: str = Form(None), category_id: int = Form(None)) -> Any:
        try:
            if not file or not file.filename:
                raise HTTPException(status_code=400, detail="File is required")

            content = await file.read()
            filename = file.filename

            if not filename or filename.strip() == "":
                raise HTTPException(status_code=400, detail="Invalid filename")
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes")
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400,
                                    detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}")

            upload_dir = settings.UPLOAD_FOLDER
            os.makedirs(upload_dir, exist_ok=True)

            base, ext = os.path.splitext(filename)
            safe_name = filename
            counter = 1
            while os.path.exists(os.path.join(upload_dir, safe_name)):
                safe_name = f"{base}_{counter}{ext}"
                counter += 1

            file_path = os.path.join(upload_dir, safe_name)
            with open(file_path, "wb") as buffer:
                buffer.write(content)

            size_bytes = os.path.getsize(file_path)
            mime_type = file.content_type or 'application/octet-stream'
            sha256 = self._file_sha256(file_path)
            storage_url = f"/{upload_dir}/{safe_name}"

            rec = File(
                category_id=category_id,
                title=title,
                original_filename=filename,
                mime_type=mime_type,
                size_bytes=size_bytes,
                storage_url=storage_url,
                sha256=sha256,
            )

            async with AsyncSessionLocal() as session:
                session.add(rec)
                await session.commit()
                await session.refresh(rec)

            return {"data": rec.to_dict(), "status": "success"}

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    def _file_sha256(self, path: str) -> str:
        try:
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ''
