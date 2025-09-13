# File Manager Plugin - Required Changes

## Current Issues Analysis

### ❌ WRONG Implementation (Current State)
The file-manager plugin has several architectural issues:

1. **Missing Plugin Configuration**: `plugin.json` has empty config `{}`
2. **Wrong Settings Access**: Router tries to use undefined `settings` instead of plugin config
3. **Missing Imports**: Router missing `File` model and `AsyncSessionLocal` imports
4. **Wrong Config Pattern**: Using non-existent `config.get()` inline defaults
5. **Missing Service Initialization**: No proper config passing to services

### ✅ CORRECT Pattern (Based on LMStudio/MusicArtist/Template Plugins)

## Required Changes

### 1. Update `plugin.json` - Add Proper Configuration
```json
{
  "name": "file-manager",
  "version": "0.5.0",
  "class": "NxWebFileManagerPlugin",
  "dependencies": ["db"],
  "config": {
    "max_file_size": 10485760,
    "allowed_extensions": [".jpg", ".png", ".pdf", ".txt", ".doc", ".docx"],
    "upload_folder": "static/uploads",
    "sha256_required": false,
    "auto_create_dirs": true,
    "filename_strategy": "safe_rename",
    "mime_validation": true
  }
}
```

### 2. Fix `plugin.py` - Use Correct Plugin Pattern
```python
from nonix_di.decorator import injectables
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from .services.file_service import FileService
from .services.file_category_service import FileCategoryService
from .services.file_link_service import FileLinkService
from .routers.file import FileRouter
from .routers.file_category import FileCategoryRouter
from .routers.file_link import FileLinkRouter

@web_routers([
    FileRouter,
    FileCategoryRouter,
    FileLinkRouter
])
@injectables([
    FileService,
    FileCategoryService,
    FileLinkService
])
class NxWebFileManagerPlugin(BasePlugin):
    # NO DI registration of plugin itself!
    # NO inline config.get() defaults!

    async def _startup(self, config: Dict[str, Any]):
        # Pass config to services through their initialize methods
        await self.file_service.initialize(config)
```

### 3. Update Services - Add Config Initialization

#### `file_service.py`:
```python
class FileService(BaseCrudService):
    def __init__(self):
        super().__init__()
        self.max_file_size = None
        self.allowed_extensions = None
        self.upload_folder = None
        self.sha256_required = None
        self.auto_create_dirs = None

    async def initialize(self, config: Dict[str, Any]):
        # Store config values directly from plugin.json
        self.max_file_size = config["max_file_size"]
        self.allowed_extensions = config["allowed_extensions"]
        self.upload_folder = config["upload_folder"]
        self.sha256_required = config["sha256_required"]
        self.auto_create_dirs = config["auto_create_dirs"]
```

#### `file_category_service.py`:
```python
class FileCategoryService(BaseCrudService):
    def __init__(self):
        super().__init__()
        # Add any config needed for categories
```

#### `file_link_service.py`:
```python
class FileLinkService(BaseCrudService):
    def __init__(self):
        super().__init__()
        # Add any config needed for links
```

### 4. Fix Router Implementation

#### `file/file_router.py` - Complete Rewrite:
```python
import hashlib
import os
from typing import Any

from fastapi import HTTPException, UploadFile, Form

from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from nonix_web_file_manager.services.file_service import FileService
from nonix_web_file_manager.models.file import File
from nonix_web_db.plugin import AsyncSessionLocal

@router("/files", tags=["Files"])
class FileRouter(NxWebServerCrudRouter):
    service: FileService = NxInject(FileService)

    @route('/upload', methods=['POST'])
    async def upload(self, file: UploadFile, title: str = Form(None), category_id: int = Form(None)) -> Any:
        try:
            if not file or not file.filename:
                raise HTTPException(status_code=400, detail="File is required")

            content = await file.read()
            filename = file.filename

            if not filename or filename.strip() == "":
                raise HTTPException(status_code=400, detail="Invalid filename")

            # Use service config values (from plugin.json)
            if len(content) > self.service.max_file_size:
                raise HTTPException(status_code=400, detail=f"File too large. Max size: {self.service.max_file_size} bytes")

            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.service.allowed_extensions:
                raise HTTPException(status_code=400,
                                    detail=f"File type not allowed. Allowed: {self.service.allowed_extensions}")

            upload_dir = self.service.upload_folder
            os.makedirs(upload_dir, exist_ok=self.service.auto_create_dirs)

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
            sha256 = self._file_sha256(file_path) if self.service.sha256_required else ''
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
```

#### `file_category/file_category_router.py`:
```python
from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from nonix_web_file_manager.services.file_category_service import FileCategoryService

@router("/file-categories", tags=["File Categories"])
class FileCategoryRouter(NxWebServerCrudRouter):
    service: FileCategoryService = NxInject(FileCategoryService)
```

#### `file_link/file_link_router.py`:
```python
from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from nonix_web_file_manager.services.file_link_service import FileLinkService

@router("/file-links", tags=["File Links"])
class FileLinkRouter(NxWebServerCrudRouter):
    service: FileLinkService = NxInject(FileLinkService)
```

### 5. Enable Plugin in `main.py`
```python
settings.PLUGINS = [
    # ... other plugins ...
    {"name": "file-manager"},  # ← UNCOMMENT THIS LINE
    # ... other plugins ...
]
```

## Implementation Order

1. **Update `plugin.json`** - Add proper configuration
2. **Fix `plugin.py`** - Use correct decorator pattern
3. **Update Services** - Add `initialize()` methods
4. **Fix Routers** - Use service config instead of undefined `settings`
5. **Enable Plugin** - Uncomment in `main.py`
6. **Test** - Verify file upload works

## Key Architectural Changes

### ❌ WRONG (Current):
- Empty plugin.json config
- Router uses undefined `settings`
- Missing imports
- No service initialization

### ✅ CORRECT (Target):
- Plugin.json has full config
- Services get config through `initialize()` method
- Router uses `self.service.config_values`
- Decorators register services/routers
- No DI registration of plugin itself
- No inline `config.get()` defaults

## Testing Checklist

- [ ] Plugin loads without errors
- [ ] File upload endpoint works
- [ ] Config values are used correctly
- [ ] File validation works
- [ ] Database operations work
- [ ] Frontend integration works

## Files to Change

1. `faster_backend/nonix_web_file_manager/plugin.json`
2. `faster_backend/nonix_web_file_manager/plugin.py`
3. `faster_backend/nonix_web_file_manager/services/file_service.py`
4. `faster_backend/nonix_web_file_manager/services/file_category_service.py`
5. `faster_backend/nonix_web_file_manager/services/file_link_service.py`
6. `faster_backend/nonix_web_file_manager/routers/file/file_router.py`
7. `faster_backend/nonix_web_file_manager/routers/file_category/file_category_router.py`
8. `faster_backend/nonix_web_file_manager/routers/file_link/file_link_router.py`
9. `faster_backend/main.py`
