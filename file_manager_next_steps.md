# File Manager Integration - Detailed Implementation Steps

## 🚀 IMMEDIATE ACTIONS

### **Phase 1: Fix Settings Configuration**

#### **Step 1.1: Add Missing Settings to Settings Class**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web/config.py`

**Action:** Add the following settings to the `Settings` class:

```python
class Settings:
    # ... existing settings ...

    # File Manager Settings
    MAX_FILE_SIZE: int = 10485760  # 10MB default
    ALLOWED_EXTENSIONS: list = [".jpg", ".png", ".pdf", ".txt", ".mp3", ".mp4", ".avi", ".mov"]
    UPLOAD_FOLDER: str = "static/uploads"
    STATIC_URL_PREFIX: str = "/static"

    # ... rest of existing settings ...
```

**Expected Result:** Settings class now has all required file management configuration.

#### **Step 1.2: Fix Settings Import in FileService**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/file/file_service.py`

**Current State:**

```python
from nonix_web.services.web_server_router import routed_service, route
from nonix_web_db import AsyncSessionLocal
```

**Action:** Add settings import:

```python
from nonix_web.services.web_server_router import routed_service, route
from nonix_web.config import settings  # ← ADD THIS LINE
from nonix_web_db import AsyncSessionLocal
```

**Expected Result:** FileService can now access `settings.MAX_FILE_SIZE`, `settings.ALLOWED_EXTENSIONS`, etc.

#### **Step 1.3: Enable File Manager Plugin**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/main.py`

**Current State:**
```python
settings.PLUGINS = [
    {"name": "cors"},
    {"name": "open-api"},
    {"name": "db"},
    {"name": "template"},
    {"name": "static-files"},
    {"name": "agentic"},
    # {"name": "file-manager"}, # settings problem
    {"name": "music-artist"},
    # {"name": "websocket"},
]
```

**Action:** Uncomment the file-manager plugin:

```python
settings.PLUGINS = [
    {"name": "cors"},
    {"name": "open-api"},
    {"name": "db"},
    {"name": "template"},
    {"name": "static-files"},
    {"name": "agentic"},
    {"name": "file-manager"},  # ← UNCOMMENT THIS LINE
    {"name": "music-artist"},
    # {"name": "websocket"},
]
```

**Expected Result:** File manager plugin will be loaded on server startup.

### **Phase 2: Create Internal Services (No Routing Decorators)**

#### **Step 2.1: Create Directory Structure**
**Directory Structure to Create:**
```
/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/internal/
├── __init__.py
├── file_service.py
└── file_link_service.py
```

**Action:** Create the `internal` directory and `__init__.py` file.

#### **Step 2.2: Create InternalFileService**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/internal/file_service.py`

**Content:**
```python
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from nonix_web_db import AsyncSessionLocal
from ...models.file import File


class InternalFileService:
    """Internal file operations for other plugins (no routing decorators)"""

    async def create_file(self, file_data: Dict[str, Any]) -> File:
        """Create a new file record"""
        async with AsyncSessionLocal() as session:
            file = File(**file_data)
            session.add(file)
            await session.commit()
            await session.refresh(file)
            return file

    async def get_file(self, file_id: int) -> Optional[File]:
        """Get file by ID"""
        async with AsyncSessionLocal() as session:
            return await session.get(File, file_id)

    async def get_files_by_ids(self, file_ids: List[int]) -> List[File]:
        """Get multiple files by IDs"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(File).where(File.id.in_(file_ids))
            )
            return result.scalars().all()

    async def update_file(self, file_id: int, updates: Dict[str, Any]) -> Optional[File]:
        """Update file metadata"""
        async with AsyncSessionLocal() as session:
            file = await session.get(File, file_id)
            if file:
                for key, value in updates.items():
                    setattr(file, key, value)
                await session.commit()
                await session.refresh(file)
            return file

    async def delete_file(self, file_id: int) -> bool:
        """Delete file by ID"""
        async with AsyncSessionLocal() as session:
            file = await session.get(File, file_id)
            if file:
                await session.delete(file)
                await session.commit()
                return True
            return False

    async def get_files_by_category(self, category_id: int) -> List[File]:
        """Get all files in a category"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(File).where(File.category_id == category_id)
            )
            return result.scalars().all()

    async def search_files(self, query: str, limit: int = 50) -> List[File]:
        """Search files by title or filename"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(File).where(
                    (File.title.ilike(f"%{query}%")) |
                    (File.original_filename.ilike(f"%{query}%"))
                ).limit(limit)
            )
            return result.scalars().all()
```

#### **Step 2.3: Create InternalFileLinkService**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/internal/file_link_service.py`

**Content:**
```python
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from nonix_web_db import AsyncSessionLocal
from ...models.file_link import FileLink


class InternalFileLinkService:
    """Internal file link operations for other plugins (no routing decorators)"""

    async def attach_file_to_entity(
        self,
        file_id: int,
        entity_type: str,
        entity_id: int,
        status: str = "attached",
        comment: str = None,
        sort_order: int = 0
    ) -> FileLink:
        """Attach a file to any entity"""
        async with AsyncSessionLocal() as session:
            link = FileLink(
                file_id=file_id,
                entity_type=entity_type,
                entity_id=entity_id,
                status=status,
                comment=comment,
                sort_order=sort_order
            )
            session.add(link)
            await session.commit()
            await session.refresh(link)
            return link

    async def attach_files_to_entity(
        self,
        file_ids: List[int],
        entity_type: str,
        entity_id: int,
        status: str = "attached",
        comment: str = None
    ) -> List[FileLink]:
        """Attach multiple files to an entity"""
        links = []
        for i, file_id in enumerate(file_ids):
            link = await self.attach_file_to_entity(
                file_id=file_id,
                entity_type=entity_type,
                entity_id=entity_id,
                status=status,
                comment=comment,
                sort_order=i
            )
            links.append(link)
        return links

    async def get_entity_files(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None
    ) -> List[FileLink]:
        """Get all file links for an entity"""
        async with AsyncSessionLocal() as session:
            query = select(FileLink).where(
                (FileLink.entity_type == entity_type) &
                (FileLink.entity_id == entity_id)
            )
            if status:
                query = query.where(FileLink.status == status)

            result = await session.execute(query)
            return result.scalars().all()

    async def get_entity_file_ids(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None
    ) -> List[int]:
        """Get file IDs attached to an entity"""
        links = await self.get_entity_files(entity_type, entity_id, status)
        return [link.file_id for link in links]

    async def detach_file_from_entity(
        self,
        file_id: int,
        entity_type: str,
        entity_id: int
    ) -> bool:
        """Detach a specific file from an entity"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(FileLink).where(
                    (FileLink.file_id == file_id) &
                    (FileLink.entity_type == entity_type) &
                    (FileLink.entity_id == entity_id)
                )
            )
            await session.commit()
            return result.rowcount > 0

    async def detach_files_from_entity(
        self,
        file_ids: List[int],
        entity_type: str,
        entity_id: int
    ) -> int:
        """Detach multiple files from an entity"""
        detached_count = 0
        for file_id in file_ids:
            if await self.detach_file_from_entity(file_id, entity_type, entity_id):
                detached_count += 1
        return detached_count

    async def cleanup_entity_files(
        self,
        entity_type: str,
        entity_id: int
    ) -> int:
        """Remove all file links for an entity (called when entity is deleted)"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(FileLink).where(
                    (FileLink.entity_type == entity_type) &
                    (FileLink.entity_id == entity_id)
                )
            )
            await session.commit()
            return result.rowcount

    async def update_file_link_status(
        self,
        file_id: int,
        entity_type: str,
        entity_id: int,
        status: str
    ) -> bool:
        """Update the status of a file link"""
        async with AsyncSessionLocal() as session:
            link = await session.execute(
                select(FileLink).where(
                    (FileLink.file_id == file_id) &
                    (FileLink.entity_type == entity_type) &
                    (FileLink.entity_id == entity_id)
                )
            )
            link = link.scalar_one_or_none()
            if link:
                link.status = status
                await session.commit()
                return True
            return False

    async def reorder_entity_files(
        self,
        entity_type: str,
        entity_id: int,
        file_id_order: List[int]
    ) -> bool:
        """Reorder files for an entity"""
        async with AsyncSessionLocal() as session:
            for order, file_id in enumerate(file_id_order):
                await session.execute(
                    update(FileLink).where(
                        (FileLink.file_id == file_id) &
                        (FileLink.entity_type == entity_type) &
                        (FileLink.entity_id == entity_id)
                    ).values(sort_order=order)
                )
            await session.commit()
            return True
```

#### **Step 2.4: Create InternalFileCategoryService**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/internal/file_category_service.py`

**Content:**
```python
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from nonix_web_db import AsyncSessionLocal
from ...models.file_category import FileCategory


class InternalFileCategoryService:
    """Internal file category operations for other plugins (no routing decorators)"""

    async def create_category(self, category_data: Dict[str, Any]) -> FileCategory:
        """Create a new file category"""
        async with AsyncSessionLocal() as session:
            category = FileCategory(**category_data)
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category

    async def get_category(self, category_id: int) -> Optional[FileCategory]:
        """Get category by ID"""
        async with AsyncSessionLocal() as session:
            return await session.get(FileCategory, category_id)

    async def get_category_by_slug(self, slug: str) -> Optional[FileCategory]:
        """Get category by slug"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(FileCategory).where(FileCategory.slug == slug)
            )
            return result.scalar_one_or_none()

    async def get_all_categories(self) -> List[FileCategory]:
        """Get all categories"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(FileCategory))
            return result.scalars().all()

    async def update_category(self, category_id: int, updates: Dict[str, Any]) -> Optional[FileCategory]:
        """Update category"""
        async with AsyncSessionLocal() as session:
            category = await session.get(FileCategory, category_id)
            if category:
                for key, value in updates.items():
                    setattr(category, key, value)
                await session.commit()
                await session.refresh(category)
            return category

    async def delete_category(self, category_id: int) -> bool:
        """Delete category by ID"""
        async with AsyncSessionLocal() as session:
            category = await session.get(FileCategory, category_id)
            if category:
                await session.delete(category)
                await session.commit()
                return True
            return False
```

### **Phase 3: Register Internal Services in DI Container**

#### **Step 3.1: Create Services __init__.py**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/__init__.py`

**Content:**
```python
# Import and register internal routers for dependency injection
from nonix_web.utils.di import di_register
from .internal.file_service import InternalFileService
from .internal.file_link_service import InternalFileLinkService
from .internal.file_category_service import InternalFileCategoryService

# Register internal routers as singletons for other plugins to inject
di_register(InternalFileService, singleton=True)
di_register(InternalFileLinkService, singleton=True)
di_register(InternalFileCategoryService, singleton=True)
```

#### **Step 3.2: Update Plugin __init__.py**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/__init__.py`

**Current State:** Empty or basic imports

**Action:** Ensure services are imported:

```python
# Import routers to ensure they are registered
from . import services
```

## 🚀 SHORT TERM ACTIONS

### **Phase 4: Create FileManagerService with High-Level Methods**

#### **Step 4.1: Create FileManagerService**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/file_manager_service.py`

**Content:**
```python
from typing import List, Dict, Any, Optional
from nonix_web.utils.di import Inject
from .internal.file_service import InternalFileService
from .internal.file_link_service import InternalFileLinkService
from .internal.file_category_service import InternalFileCategoryService


class FileManagerService:
    """
    High-level service for generic file management across plugins.
    This service provides easy-to-use methods for other plugins to manage files.
    """

    file_service: InternalFileService = Inject(InternalFileService)
    file_link_service: InternalFileLinkService = Inject(InternalFileLinkService)
    file_category_service: InternalFileCategoryService = Inject(InternalFileCategoryService)

    # === FILE OPERATIONS ===

    async def create_file(self, file_data: Dict[str, Any]) -> Any:
        """Create a new file record"""
        return await self.file_service.create_file(file_data)

    async def get_file(self, file_id: int) -> Optional[Any]:
        """Get file by ID"""
        return await self.file_service.get_file(file_id)

    async def update_file(self, file_id: int, updates: Dict[str, Any]) -> Optional[Any]:
        """Update file metadata"""
        return await self.file_service.update_file(file_id, updates)

    async def delete_file(self, file_id: int) -> bool:
        """Delete file by ID"""
        return await self.file_service.delete_file(file_id)

    # === FILE ATTACHMENT OPERATIONS ===

    async def attach_files_to_entity(
        self,
        entity_type: str,
        entity_id: int,
        file_ids: List[int],
        status: str = "attached",
        comment: str = None
    ) -> List[int]:
        """
        Attach multiple files to any entity.
        Returns list of created link IDs.
        """
        links = await self.file_link_service.attach_files_to_entity(
            file_ids, entity_type, entity_id, status, comment
        )
        return [link.id for link in links]

    async def attach_file_to_entity(
        self,
        entity_type: str,
        entity_id: int,
        file_id: int,
        status: str = "attached",
        comment: str = None
    ) -> int:
        """
        Attach a single file to any entity.
        Returns the created link ID.
        """
        link = await self.file_link_service.attach_file_to_entity(
            file_id, entity_type, entity_id, status, comment
        )
        return link.id

    async def get_entity_files(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None,
        include_file_details: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all files attached to an entity.
        If include_file_details=True, returns file objects with link info.
        """
        links = await self.file_link_service.get_entity_files(
            entity_type, entity_id, status
        )

        if not include_file_details:
            return [{"link": link, "file": None} for link in links]

        result = []
        for link in links:
            file = await self.file_service.get_file(link.file_id)
            result.append({
                "file": file,
                "link": link
            })

        return result

    async def get_entity_file_ids(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None
    ) -> List[int]:
        """Get just the file IDs attached to an entity"""
        return await self.file_link_service.get_entity_file_ids(
            entity_type, entity_id, status
        )

    async def detach_files_from_entity(
        self,
        entity_type: str,
        entity_id: int,
        file_ids: List[int] = None,
        status: str = None
    ) -> int:
        """
        Detach files from entity.
        If file_ids=None, detaches all files.
        If status specified, only detaches files with that status.
        Returns number of files detached.
        """
        if file_ids:
            return await self.file_link_service.detach_files_from_entity(
                file_ids, entity_type, entity_id
            )
        else:
            # Detach all files (optionally filtered by status)
            if status:
                links = await self.file_link_service.get_entity_files(
                    entity_type, entity_id, status
                )
                file_ids = [link.file_id for link in links]

            return await self.file_link_service.detach_files_from_entity(
                file_ids, entity_type, entity_id
            )

    async def detach_file_from_entity(
        self,
        entity_type: str,
        entity_id: int,
        file_id: int
    ) -> bool:
        """Detach a specific file from an entity"""
        return await self.file_link_service.detach_file_from_entity(
            file_id, entity_type, entity_id
        )

    # === CLEANUP OPERATIONS ===

    async def cleanup_orphaned_files(
        self,
        entity_type: str,
        entity_id: int
    ) -> int:
        """
        Remove all file links for an entity.
        Called when entity is deleted to prevent orphaned links.
        Returns number of links removed.
        """
        return await self.file_link_service.cleanup_entity_files(
            entity_type, entity_id
        )

    async def cleanup_entity_and_files(
        self,
        entity_type: str,
        entity_id: int,
        delete_files: bool = False
    ) -> Dict[str, int]:
        """
        Cleanup both entity links and optionally files themselves.
        Returns counts of what was cleaned up.
        """
        links_removed = await self.cleanup_orphaned_files(entity_type, entity_id)

        files_deleted = 0
        if delete_files:
            file_ids = await self.get_entity_file_ids(entity_type, entity_id)
            for file_id in file_ids:
                if await self.delete_file(file_id):
                    files_deleted += 1

        return {
            "links_removed": links_removed,
            "files_deleted": files_deleted
        }

    # === STATUS MANAGEMENT ===

    async def update_file_status(
        self,
        entity_type: str,
        entity_id: int,
        file_id: int,
        status: str
    ) -> bool:
        """Update the status of a file attachment"""
        return await self.file_link_service.update_file_link_status(
            file_id, entity_type, entity_id, status
        )

    async def set_primary_file(
        self,
        entity_type: str,
        entity_id: int,
        file_id: int
    ) -> bool:
        """Set a file as primary (status='primary') and others as 'attached'"""
        # First, set all files to 'attached'
        links = await self.file_link_service.get_entity_files(entity_type, entity_id)
        for link in links:
            await self.file_link_service.update_file_link_status(
                link.file_id, entity_type, entity_id, "attached"
            )

        # Then set the primary file
        return await self.update_file_status(entity_type, entity_id, file_id, "primary")

    # === CATEGORY OPERATIONS ===

    async def get_category(self, category_id: int) -> Optional[Any]:
        """Get file category by ID"""
        return await self.file_category_service.get_category(category_id)

    async def get_category_by_slug(self, slug: str) -> Optional[Any]:
        """Get file category by slug"""
        return await self.file_category_service.get_category_by_slug(slug)

    async def get_all_categories(self) -> List[Any]:
        """Get all file categories"""
        return await self.file_category_service.get_all_categories()

    # === UTILITY METHODS ===

    async def get_entity_file_count(
        self,
        entity_type: str,
        entity_id: int,
        status: str = None
    ) -> int:
        """Get count of files attached to an entity"""
        file_ids = await self.get_entity_file_ids(entity_type, entity_id, status)
        return len(file_ids)

    async def entity_has_file(
        self,
        entity_type: str,
        entity_id: int,
        file_id: int
    ) -> bool:
        """Check if entity has a specific file attached"""
        file_ids = await self.get_entity_file_ids(entity_type, entity_id)
        return file_id in file_ids

    async def get_entity_primary_file(
        self,
        entity_type: str,
        entity_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get the primary file for an entity (status='primary')"""
        files = await self.get_entity_files(entity_type, entity_id, status="primary")
        return files[0] if files else None
```

#### **Step 4.2: Register FileManagerService**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_file_manager/services/__init__.py`

**Action:** Update the services __init__.py:

```python
# Import and register internal routers for dependency injection
from nonix_web.utils.di import di_register
from .internal.file_service import InternalFileService
from .internal.file_link_service import InternalFileLinkService
from .internal.file_category_service import InternalFileCategoryService
from .file_manager_service import FileManagerService  # ← ADD THIS

# Register internal routers as singletons for other plugins to inject
di_register(InternalFileService, singleton=True)
di_register(InternalFileLinkService, singleton=True)
di_register(InternalFileCategoryService, singleton=True)
di_register(FileManagerService, singleton=True)  # ← ADD THIS
```

### **Phase 5: Integrate with AlbumService as Example**

#### **Step 5.1: Examine AlbumService Structure**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_music_artist/services/album/album_service.py`

**Current Content Analysis:**

```python
from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig,
    NxWebServerCrudRouter
from .album_schemas import AlbumCreate, AlbumUpdate, AlbumInDbModel
from ...models.album import Album


@routed_service("/albums", tags=["Albums"])
class AlbumService(NxWebServerCrudRouter):
# CRUD configuration for albums
```

#### **Step 5.2: Add FileManagerService Integration**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_music_artist/services/album/album_service.py`

**Action:** Add FileManagerService injection and file management methods:

```python
from nonix_web.services.web_server_router import routed_service
from nonix_web.utils.di import Inject  # ← ADD THIS IMPORT
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig,
    NxWebServerCrudRouter
from .album_schemas import AlbumCreate, AlbumUpdate, AlbumInDbModel
from ...models.album import Album

# ADD THIS: Import the FileManagerService
from nonix_web_file_manager.services.file_manager_service import FileManagerService


@routed_service("/albums", tags=["Albums"])
class AlbumService(NxWebServerCrudRouter):
    # ADD THIS: Inject FileManagerService
    file_manager: FileManagerService = Inject(FileManagerService)

    config = CRUDConfig(
        model=Album,
        create_schema=AlbumCreate,
        update_schema=AlbumUpdate,
        response_schema=AlbumInDbModel,
        filters=FilterConfig(
            allowed_fields=['title', 'release_date', 'artist_id']
        ),
        sorting=SortingConfig(
            default_sort='release_date',
            allowed_fields=['title', 'release_date', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['title', 'release_date'],
            display_format='{title}',
            search_fields=['title']
        )
    )

    # ADD THIS: Method to create album with cover file
    async def create_album_with_cover(
            self,
            album_data: dict,
            cover_file_id: int = None
    ) -> Album:
        """
        Create an album and optionally attach a cover file.
        """
        # Create the album first
        album = await self.create(album_data)

        # If cover file provided, attach it
        if cover_file_id:
            await self.file_manager.attach_file_to_entity(
                entity_type="album",
                entity_id=album.id,
                file_id=cover_file_id,
                status="cover"
            )

        return album

    # ADD THIS: Method to get album with file information
    async def get_album_with_files(
            self,
            album_id: int
    ) -> dict:
        """
        Get album with all attached files.
        """
        # Get the album
        album = await self.get(album_id)
        if not album:
            return None

        # Get all files attached to this album
        files = await self.file_manager.get_entity_files(
            entity_type="album",
            entity_id=album_id
        )

        # Separate cover and other files
        cover_files = [f for f in files if f.get('link') and f['link'].status == 'cover']
        other_files = [f for f in files if f.get('link') and f['link'].status != 'cover']

        return {
            "album": album,
            "cover_files": cover_files,
            "other_files": other_files,
            "total_files": len(files)
        }

    # ADD THIS: Method to update album cover
    async def update_album_cover(
            self,
            album_id: int,
            new_cover_file_id: int
    ) -> bool:
        """
        Update album cover (replaces existing cover).
        """
        # Remove existing cover files
        existing_cover_files = await self.file_manager.get_entity_files(
            entity_type="album",
            entity_id=album_id,
            status="cover"
        )

        if existing_cover_files:
            existing_file_ids = [f['link'].file_id for f in existing_cover_files]
            await self.file_manager.detach_files_from_entity(
                entity_type="album",
                entity_id=album_id,
                file_ids=existing_file_ids
            )

        # Attach new cover
        await self.file_manager.attach_file_to_entity(
            entity_type="album",
            entity_id=album_id,
            file_id=new_cover_file_id,
            status="cover"
        )

        return True

    # ADD THIS: Method to attach additional files
    async def attach_files_to_album(
            self,
            album_id: int,
            file_ids: list,
            status: str = "attached"
    ) -> int:
        """
        Attach multiple files to an album.
        """
        return len(await self.file_manager.attach_files_to_entity(
            entity_type="album",
            entity_id=album_id,
            file_ids=file_ids,
            status=status
        ))

    # ADD THIS: Override delete method to cleanup files
    async def delete_album(self, album_id: int) -> bool:
        """
        Delete album and cleanup all attached files.
        """
        # Cleanup file links (but keep files themselves)
        await self.file_manager.cleanup_orphaned_files(
            entity_type="album",
            entity_id=album_id
        )

        # Delete the album
        return await self.delete(album_id)

    # ADD THIS: Method to get album statistics
    async def get_album_file_stats(self, album_id: int) -> dict:
        """
        Get file statistics for an album.
        """
        total_files = await self.file_manager.get_entity_file_count("album", album_id)

        files = await self.file_manager.get_entity_files("album", album_id)
        status_counts = {}
        for file_info in files:
            status = file_info.get('link', {}).status or 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "album_id": album_id,
            "total_files": total_files,
            "status_breakdown": status_counts,
            "has_cover": status_counts.get('cover', 0) > 0
        }
```

#### **Step 5.3: Add File Management Routes**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_music_artist/services/album/album_service.py`

**Action:** Add optional API routes for file management:

```python
# ... existing code ...

@route('/{album_id}/files', methods=['GET'])
async def get_album_files(self, album_id: int):
    """Get all files attached to an album"""
    return await self.get_album_with_files(album_id)

@route('/{album_id}/files', methods=['POST'])
async def attach_files_to_album_route(self, album_id: int, file_ids: list, status: str = "attached"):
    """Attach files to an album via API"""
    count = await self.attach_files_to_album(album_id, file_ids, status)
    return {"message": f"Attached {count} files to album {album_id}"}

@route('/{album_id}/cover', methods=['PUT'])
async def update_album_cover_route(self, album_id: int, cover_file_id: int):
    """Update album cover via API"""
    success = await self.update_album_cover(album_id, cover_file_id)
    return {"success": success, "message": "Cover updated"}

@route('/{album_id}/files/{file_id}', methods=['DELETE'])
async def detach_file_from_album(self, album_id: int, file_id: int):
    """Detach a specific file from an album"""
    success = await self.file_manager.detach_file_from_entity(
        entity_type="album",
        entity_id=album_id,
        file_id=file_id
    )
    return {"success": success}
```

#### **Step 5.4: Update Album Schemas**
**File:** `/home/dex/Desktop/shadewalk/4Real/faster_backend/nonix_web_music_artist/services/album/album_schemas.py`

**Action:** Add file-related fields to response schemas if needed:

```python
# In AlbumInDbModel, you could add computed fields:
class AlbumInDbModel(AlbumBase, BaseDbModelMixin):
    file_count: int = Field(default=0)
    has_cover: bool = Field(default=False)
    # ... other fields
```

## 📋 VERIFICATION STEPS

### **After Implementation:**

1. **Start Server**: Run the server and verify file-manager plugin loads
2. **Check Logs**: Look for successful plugin initialization
3. **Test Injection**: Verify other plugins can inject FileManagerService
4. **Test Album Integration**: Create album with cover file
5. **Verify API**: Test both internal methods and external API routes

### **Expected Results:**

- ✅ FileManagerService can be injected in any plugin
- ✅ Albums can have cover files and attachments
- ✅ File links are automatically cleaned up when entities are deleted
- ✅ External API still works for file management
- ✅ Internal plugin communication works seamlessly

---

**Implementation Time Estimate**: 4-6 hours for all phases
**Priority**: High - Enables generic file management across all plugins
**Dependencies**: Settings configuration must be completed first
