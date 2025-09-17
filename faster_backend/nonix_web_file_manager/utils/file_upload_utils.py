import hashlib
import os
from typing import Any, Dict
from fastapi import HTTPException, UploadFile
from nonix_web_db.plugin import AsyncSessionLocal
from ..models.file import File


async def upload_file_logic(
    file: UploadFile, 
    title: str, 
    category_id: int, 
    service
) -> Dict[str, Any]:
    """Complete file upload logic extracted from FileRouter"""
    try:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="File is required")

        content = await file.read()
        filename = file.filename

        if not filename or filename.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid filename")

        if service.max_file_size is not None and len(content) > service.max_file_size:
            raise HTTPException(status_code=400, detail=f"File too large. Max: {service.max_file_size} bytes")

        file_ext = os.path.splitext(filename)[1].lower()
        if service.allowed_extensions is not None and file_ext not in service.allowed_extensions:
            raise HTTPException(status_code=400,
                                detail=f"File type not allowed. Allowed: {service.allowed_extensions}")

        upload_dir = service.upload_folder
        os.makedirs(upload_dir, exist_ok=service.auto_create_dirs)

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
        sha256 = _file_sha256(file_path) if service.sha256_required else ''
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


def _file_sha256(path: str) -> str:
    """Calculate SHA256 hash of file"""
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ''
