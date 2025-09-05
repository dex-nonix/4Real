# File Manager Integration Analysis & Roadmap

## 📊 Current Status Overview

### ✅ **WHAT ALREADY EXISTS**

#### **Backend Models & Services (Complete & Ready)**
1. **`File` Model** (`nonix_web_file_manager/models/file.py`):
   - Complete with all necessary fields: title, filename, MIME type, size, SHA256, dimensions, storage URL
   - Proper relationships with FileCategory

2. **`FileLink` Model** (`nonix_web_file_manager/models/file_link.py`):
   - **Perfect generic design** with `entity_type` and `entity_id` fields for any table attachment
   - Includes status, comment, sort_order fields
   - Proper cascade delete: `cascade='all, delete-orphan'`

3. **`FileCategory` Model** (`nonix_web_file_manager/models/file_category.py`):
   - Ready for file organization with name, slug, description

#### **🔥 CRITICAL INSIGHT: ROUTED vs INTERNAL SERVICES**

The existing services are **API ROUTED SERVICES** (for external HTTP access):
```python
@router("/files", tags=["Files"])  # ← EXTERNAL API ROUTES
class FileRouter(NxWebServerCrudRouter):
    # This creates HTTP endpoints like GET /api/files
    # Used by frontend, external clients, etc.
```

**BUT WE'RE MISSING INTERNAL SERVICES** for plugin-to-plugin communication:
```python
class InternalFileService:  # ← INTERNAL SERVICE (no routing)
    # Direct method calls for other plugins
    async def create_file(self, data): ...
    async def get_file(self, file_id): ...
```

### ❌ **WHAT'S MISSING/BROKEN**

#### **Critical Issues**
1. **Missing Settings Configuration**:
   - `FileRouter.upload()` references undefined settings:
     - `settings.MAX_FILE_SIZE`
     - `settings.ALLOWED_EXTENSIONS`
     - `settings.UPLOAD_FOLDER`
   - `upload.py` also references these same undefined settings
   - **File manager plugin is commented out** in `main.py` due to this issue

2. **Missing Settings Import**:
   - File service doesn't import settings but references them

#### **🚨 MISSING: Internal Services for Plugin Communication**
1. **No Internal File Service**:
   - Other plugins can't inject and use file operations directly
   - No `InternalFileService` without routing decorators

2. **No Internal FileLink Service**:
   - No `InternalFileLinkService` for attaching/detaching files

3. **No FileManagerService**:
   - No high-level service that other plugins can easily inject and use
   - Missing helper methods like:
     - `attachFilesToEntity()`
     - `getEntityFiles()`
     - `detachFilesFromEntity()`
     - `cleanupOrphanedFiles()`

## 🚀 **CORRECTED IMPLEMENTATION ROADMAP**

### **Phase 1: Fix Critical Issues (1-2 hours)**
1. **Add missing settings to `Settings` class**:
   ```python
   # Add to nonix_web/config.py
   MAX_FILE_SIZE: int = 10485760  # 10MB
   ALLOWED_EXTENSIONS: list = [".jpg", ".png", ".pdf", ".txt", ".mp3", ".mp4"]
   UPLOAD_FOLDER: str = "static/uploads"
   STATIC_URL_PREFIX: str = "/static"
   ```

2. **Fix settings import in FileRouter**:
   ```python
   # Add to file_router.py
   from ..config import settings
   ```

3. **Enable file-manager plugin**:
   - Uncomment `{"name": "file-manager"}` in `main.py`

### **Phase 2: Create Internal Services (3-4 hours)**
Create internal services that other plugins can inject:

```python
# nonix_web_file_manager/routers/internal/file_router.py
from typing import List, Optional
from nonix_web_db import AsyncSessionLocal
from ...models.file import File

class InternalFileService:
    """Internal file operations for other plugins (no routing)"""

    async def create_file(self, file_data: dict) -> File:
        async with AsyncSessionLocal() as session:
            file = File(**file_data)
            session.add(file)
            await session.commit()
            await session.refresh(file)
            return file

    async def get_file(self, file_id: int) -> Optional[File]:
        async with AsyncSessionLocal() as session:
            return await session.get(File, file_id)

    async def update_file(self, file_id: int, updates: dict) -> Optional[File]:
        async with AsyncSessionLocal() as session:
            file = await session.get(File, file_id)
            if file:
                for key, value in updates.items():
                    setattr(file, key, value)
                await session.commit()
                await session.refresh(file)
            return file

    async def delete_file(self, file_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            file = await session.get(File, file_id)
            if file:
                await session.delete(file)
                await session.commit()
                return True
            return False
```

```python
# nonix_web_file_manager/routers/internal/file_link_service.py
from typing import List, Optional
from nonix_web_db import AsyncSessionLocal
from ...models.file_link import FileLink

class InternalFileLinkService:
    """Internal file link operations for other plugins (no routing)"""

    async def attach_file_to_entity(
        self,
        file_id: int,
        entity_type: str,
        entity_id: int,
        status: str = "attached",
        comment: str = None
    ) -> FileLink:
        async with AsyncSessionLocal() as session:
            link = FileLink(
                file_id=file_id,
                entity_type=entity_type,
                entity_id=entity_id,
                status=status,
                comment=comment
            )
            session.add(link)
            await session.commit()
            await session.refresh(link)
            return link

    async def get_entity_files(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None
    ) -> List[FileLink]:
        async with AsyncSessionLocal() as session:
            query = session.query(FileLink).filter(
                FileLink.entity_type == entity_type,
                FileLink.entity_id == entity_id
            )
            if status:
                query = query.filter(FileLink.status == status)
            return await query.all()

    async def detach_file_from_entity(
        self,
        file_id: int,
        entity_type: str,
        entity_id: int
    ) -> bool:
        async with AsyncSessionLocal() as session:
            link = await session.query(FileLink).filter(
                FileLink.file_id == file_id,
                FileLink.entity_type == entity_type,
                FileLink.entity_id == entity_id
            ).first()
            if link:
                await session.delete(link)
                await session.commit()
                return True
            return False

    async def cleanup_entity_files(
        self,
        entity_type: str,
        entity_id: int
    ) -> int:
        """Remove all file links for an entity (called when entity is deleted)"""
        async with AsyncSessionLocal() as session:
            result = await session.query(FileLink).filter(
                FileLink.entity_type == entity_type,
                FileLink.entity_id == entity_id
            ).delete()
            await session.commit()
            return result
```

### **Phase 3: Create FileManagerService (2-3 hours)**
```python
# nonix_web_file_manager/routers/file_manager_service.py
from typing import List
from nonix_web.utils.di import Inject
from .internal.file_service import InternalFileService
from .internal.file_link_service import InternalFileLinkService

class FileManagerService:
    """High-level service for generic file management across plugins"""

    file_service: InternalFileService = Inject(InternalFileService)
    file_link_service: InternalFileLinkService = Inject(InternalFileLinkService)

    async def attach_files_to_entity(
        self,
        entity_type: str,
        entity_id: int,
        file_ids: List[int],
        status: str = "attached"
    ) -> List[int]:
        """Attach multiple files to any entity"""
        attached_ids = []
        for file_id in file_ids:
            link = await self.file_link_service.attach_file_to_entity(
                file_id, entity_type, entity_id, status
            )
            attached_ids.append(link.id)
        return attached_ids

    async def get_entity_files(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None
    ) -> List[dict]:
        """Get all files attached to an entity with file details"""
        links = await self.file_link_service.get_entity_files(
            entity_type, entity_id, status
        )

        files = []
        for link in links:
            file = await self.file_service.get_file(link.file_id)
            if file:
                files.append({
                    'file': file,
                    'link': link
                })
        return files

    async def detach_files_from_entity(
        self,
        entity_type: str,
        entity_id: int,
        file_ids: List[int] = None
    ) -> int:
        """Detach files from entity (all or specific)"""
        if file_ids:
            detached = 0
            for file_id in file_ids:
                if await self.file_link_service.detach_file_from_entity(
                    file_id, entity_type, entity_id
                ):
                    detached += 1
            return detached
        else:
            # Detach all files
            return await self.file_link_service.cleanup_entity_files(
                entity_type, entity_id
            )

    async def cleanup_orphaned_files(
        self,
        entity_type: str,
        entity_id: int
    ) -> int:
        """Called when entity is deleted"""
        return await self.file_link_service.cleanup_entity_files(
            entity_type, entity_id
        )
```

### **Phase 4: Register Internal Services (1 hour)**
```python
# nonix_web_file_manager/routers/__init__.py
from nonix_web.utils.di import di_register
from .internal.file_service import InternalFileService
from .internal.file_link_service import InternalFileLinkService
from .file_manager_service import FileManagerService

# Register internal routers for other plugins to inject
di_register(InternalFileService, singleton=True)
di_register(InternalFileLinkService, singleton=True)
di_register(FileManagerService, singleton=True)
```

### **Phase 5: Plugin Integration Example (1 hour)**
```python
# In any other plugin service
from nonix_web.utils.di import Inject
from nonix_web_file_manager.services.file_manager_service import FileManagerService

class AlbumRouter(NxWebServerCrudRouter):
    file_manager: FileManagerService = Inject(FileManagerService)

    async def create_album_with_cover(self, album_data, cover_file_id=None):
        album = await self.create(album_data)

        if cover_file_id:
            await self.file_manager.attach_files_to_entity(
                "album", album.id, [cover_file_id], status="cover"
            )

        return album

    async def delete_album(self, album_id: int):
        # Clean up files first
        await self.file_manager.cleanup_orphaned_files("album", album_id)

        # Then delete album
        return await self.delete(album_id)
```

## 🔧 **ARCHITECTURE CORRECTION**

### **Dual-Service Architecture**
```
┌─────────────────┐    ┌──────────────────┐
│   EXTERNAL API  │    │ INTERNAL SERVICES│
│   (HTTP Routes) │    │  (Plugin Inject) │
├─────────────────┤    ├──────────────────┤
│ FileRouter     │    │ InternalFileSvc  │
│ (/api/files)    │◄──►│ (Direct Methods) │
│                 │    │                  │
│ FileLinkRouter │    │ InternalFileLink │
│ (/api/file-links│◄──►│ (Direct Methods) │
│                 │    │                  │
│ FileCategorySvc │    │ InternalFileCat  │
│ (/api/categories│◄──►│ (Direct Methods) │
└─────────────────┘    └──────────────────┘
         │                       │
         ▼                       ▼
    Frontend/Vue.js        Other Plugins
```

### **Key Differences**
| Aspect | Routed Service | Internal Service |
|--------|----------------|------------------|
| **Decorator** | `@router` | None |
| **Purpose** | HTTP API endpoints | Plugin-to-plugin communication |
| **Usage** | `axios.get('/api/files')` | `service = Inject(MyService)` |
| **Return** | JSON responses | Python objects |
| **Error Handling** | HTTP status codes | Exceptions |

## 📈 **Benefits of This Architecture**

1. **Separation of Concerns**: External API vs Internal Logic
2. **Reusable**: Internal services can be used by any plugin
3. **Testable**: Internal services are easier to unit test
4. **Flexible**: Can change API without breaking internal usage
5. **Performance**: Direct method calls vs HTTP overhead

## 🎯 **Next Steps**

### **Immediate Actions (Today)**
1. Fix settings configuration
2. Create internal services (no routing decorators)
3. Register internal services in DI container
4. Test internal service injection

### **Short Term (This Week)**
1. Create FileManagerService with high-level methods
2. Integrate with AlbumRouter as example
3. Test cross-plugin file attachment

### **Medium Term (Next Month)**
1. Add file versioning and metadata
2. Implement usage analytics
3. Create admin interface

## 📝 **Current Blockers**

1. **Settings Configuration**: Must be fixed before file manager can run
2. **Missing Internal Services**: No way for plugins to communicate internally
3. **Architecture Confusion**: Mixed up routed vs internal service purposes
4. **DI Registration**: Internal services need to be registered for injection

---

**Last Updated**: $(date)
**Status**: Analysis Corrected, Ready for Proper Implementation