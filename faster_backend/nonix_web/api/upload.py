import os

import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from ..config import settings

router = APIRouter()


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in settings.ALLOWED_EXTENSIONS


def build_file_url(filename: str) -> str:
    """Build the public URL for a file."""
    return f"{settings.STATIC_URL_PREFIX}/{filename}"


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Get config values once since used multiple times
    max_file_size = settings.MAX_FILE_SIZE
    
    if file.size and file.size > max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {max_file_size // (1024 * 1024)}MB"
        )

    # Get config values once since used multiple times
    upload_folder = settings.UPLOAD_FOLDER
    
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        return {
            "filename": file.filename,
            "size": len(content),
            "path": build_file_url(file.filename),
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/files")
async def list_files():
    try:
        # Get config values once since used multiple times
        upload_folder = settings.UPLOAD_FOLDER
        
        os.makedirs(upload_folder, exist_ok=True)
        files = []

        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": build_file_url(filename)
                })

        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.get("/files/{filename}")
async def get_file(filename: str):
    # Get config values once since used multiple times
    upload_folder = settings.UPLOAD_FOLDER
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename)
