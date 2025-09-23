# FILE MANAGER INTEGRATION - SIMPLE IMPLEMENTATION

## THE PROBLEM
- File manager integration is at 0% completion
- File download/preview/stream URLs are 404 because they hit wrong router
- API is overcomplicated with multiple endpoints and methods
- Frontend uses complex URL construction instead of direct links

## THE SOLUTION
- Backend returns ONE FULL URL field per file (no storage_url in response)
- URLs are complete absolute URLs: `https://server.com/static/uploads/file.jpg`
- Frontend uses `file.url` directly in HTML - no JavaScript complexity
- Files download normally through browser links like any website

## BACKEND CHANGES

### 1. Add FileManager Response Models
**File:** `faster_backend/nonix_web_file_manager/routers/file_manager_router.py`

Add at top of file:
```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class FileManagerFileResponse(BaseModel):
    """File Manager specific response - ONE URL FIELD ONLY - NO storage_url"""
    id: int
    category_id: Optional[int] = None
    title: Optional[str] = None
    original_filename: str
    mime_type: str
    size_bytes: int
    url: str  # THIS IS THE ONLY URL FIELD - direct file URL for browser
    sha256: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None

    @classmethod
    def from_file_data(cls, file_data, base_url: str):
        """Compute FULL URL from storage_url"""
        if file_data.storage_url.startswith(('http://', 'https://')):
            computed_url = file_data.storage_url  # External URL already full
        else:
            # Generate FULL URL for local files
            computed_url = f"{base_url}/static/uploads/{os.path.basename(file_data.storage_url)}"

        return cls(
            id=file_data.id,
            category_id=file_data.category_id,
            title=file_data.title,
            original_filename=file_data.original_filename,
            mime_type=file_data.mime_type,
            size_bytes=file_data.size_bytes,
            url=computed_url,  # FULL URL ONLY
            sha256=file_data.sha256,
            width=file_data.width,
            height=file_data.height,
            duration_seconds=file_data.duration_seconds
        )

class FileManagerListResponse(BaseModel):
    """File Manager list response - PYDANTIC MODEL - NO DICTIONARY"""
    data: List[FileManagerFileResponse]
    pagination: Dict[str, Any]
```

### 2. Update list_files endpoint to return pydantic models
**File:** `faster_backend/nonix_web_file_manager/routers/file_manager_router.py`

Replace the existing list_files method:
```python
@route('/files', methods=['GET'])
async def list_files(self, req: Request):
    """List files with FULL URLs - RETURNS PYDANTIC MODEL - NO DICTIONARY"""
    # Build FULL base URL from request
    base_url = f"{req.url.scheme}://{req.url.netloc}"

    results = await self.file_service.get_all(await process_query(self.file_service, req))
    response_data = [FileManagerFileResponse.from_file_data(item, base_url) for item in results["data"]]
    return FileManagerListResponse(
        data=response_data,
        pagination=results.get("pagination", {})
    )  # RETURNS PYDANTIC MODEL - NOT DICTIONARY
```

### 3. Add single file endpoint
**File:** `faster_backend/nonix_web_file_manager/routers/file_manager_router.py`

Add after list_files method:
```python
@route('/files/{file_id}', methods=['GET'])
async def get_file_info(self, file_id: int, req: Request):
    """Get single file info with FULL URL - RETURNS PYDANTIC MODEL DIRECTLY - NO DICTIONARIES"""
    file_data = await self.file_service.get_one(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    # Build FULL base URL from request
    base_url = f"{req.url.scheme}://{req.url.netloc}"
    return FileManagerFileResponse.from_file_data(file_data, base_url)  # RETURNS PYDANTIC MODEL WITH FULL URL - NOT DICTIONARY
```

### 4. Remove old endpoints
**File:** `faster_backend/nonix_web_file_manager/routers/file_manager_router.py`

Remove these methods:
- `@route('/files/{file_id}/download', methods=['GET'])`
- `@route('/files/{file_id}/preview', methods=['GET'])`
- `@route('/files/{file_id}/stream', methods=['GET'])`

## FRONTEND CHANGES

### 1. Update NxFileManagerService.js
**File:** `vue_libs/nonix-file-manager/services/NxFileManagerService.js`

Remove all complex URL construction methods - keep only simple CRUD operations:

**REMOVE these methods:**
```javascript
// REMOVE - complex URL construction
async downloadFile(fileId) {
    const url = this.buildUrl(`/files/${fileId}/download`);
    window.open(url, '_blank');
}

async getFileUrl(fileId, action = 'preview') {
    return this.buildUrl(`/files/${fileId}/${action}`);
}

async getPreviewUrl(fileId) {
    return this.getFileUrl(fileId, 'preview');
}

async getStreamUrl(fileId) {
    return this.getFileUrl(fileId, 'stream');
}
```

**KEEP these simple methods:**
```javascript
// KEEP - simple CRUD operations
async listFiles(params = {}) {
    return this.get('/files', params);
}

async getFile(fileId) {
    return this.get(`/files/${fileId}`);
}

async deleteFile(fileId) {
    return this.delete(`/files/${fileId}`);
}

async uploadFile(formData) {
    return this.post('/upload', formData);
}

// ... other CRUD methods remain unchanged
```

### 2. Update Vue Components - Direct HTML Usage
**Find and update ALL Vue components that use file manager:**

**BEFORE - Complex service calls:**
```vue
<!-- OLD - Download button with service call -->
<button @click="downloadFile(file)">Download</button>

<!-- OLD - Image preview with service call -->
<img :src="getPreviewUrl(file.id)" alt="Preview" />

<!-- OLD - Video player with service call -->
<video :src="getStreamUrl(file.id)" controls></video>
```

**AFTER - Direct HTML with file.url:**
```vue
<!-- NEW - Direct download link -->
<a :href="file.url" download>{{ file.original_filename }}</a>

<!-- NEW - Direct image src -->
<img :src="file.url" alt="Preview" />

<!-- NEW - Direct video src -->
<video :src="file.url" controls></video>
```

**COMPLETE LIST OF FILES TO UPDATE:**

**Vue Components:**
- `vue_libs/nonix-file-manager/NxFileManager.vue` (main file manager component)
- `vue_libs/nonix-file-manager/components/NxFileListView.vue` (file list display)
- `vue_libs/nonix-file-manager/components/NxFilePreview.vue` (file preview component)
- `vue_libs/nonix-file-manager/components/NxFilePreviewPane.vue` (preview pane)
- `vue_libs/nonix-file-manager/components/NxFileTree.vue` (file tree navigation)
- `vue_libs/nonix-file-manager/components/NxFileUploadField.vue` (upload field)
- `vue_libs/nonix-file-manager/components/NxFileUploadArea.vue` (upload area)

**Service Files:**
- `vue_libs/nonix-file-manager/services/NxFileManagerService.js` (remove URL methods)

**Backend Files:**
- `faster_backend/nonix_web_file_manager/routers/file_manager_router.py` (add response models, update endpoints, remove old endpoints)

### 3. Update Component Methods
**Remove these method calls from Vue components:**
```javascript
// REMOVE from component methods:
downloadFile(file) {
    return this.fileService.downloadFile(file.id);
}

getPreviewUrl(fileId) {
    return this.fileService.getPreviewUrl(fileId);
}

getStreamUrl(fileId) {
    return this.fileService.getStreamUrl(fileId);
}
```

**Components will now use file.url directly in templates - no method calls needed.**

## TESTING

### Backend Tests
- `/api/file-manager/files` returns `FileManagerListResponse` pydantic model (NOT dictionary) with FULL URLs in each file's `url` field
- `/api/file-manager/files/{id}` returns `FileManagerFileResponse` pydantic model directly (NOT dictionary) with FULL URL in `url` field
- URLs are complete: `https://dev.local/static/uploads/filename.ext` (NOT relative `/static/uploads/...`)
- External files return their full external URLs: `https://cdn.example.com/files/file.jpg`
- No download/preview/stream endpoints exist
- ALL routes return pydantic models - never dictionaries

### Frontend Tests
- Components use `file.url` directly in HTML
- Downloads work through normal browser links
- Images/videos display using direct `src` attribute

## COMPLETE CHANGE SUMMARY

**ALL CHANGES REQUIRED:**

### Backend (1 file):
1. `faster_backend/nonix_web_file_manager/routers/file_manager_router.py`
   - Add `FileManagerFileResponse` and `FileManagerListResponse` pydantic models
   - Generate FULL URLs using `req.url.scheme + req.url.netloc`
   - Update `list_files()` to return `FileManagerListResponse` with FULL URLs (pydantic model)
   - Add `get_file_info()` endpoint returning `FileManagerFileResponse` with FULL URL (pydantic model)
   - Remove `download/preview/stream` endpoints

### Frontend Service (1 file):
2. `vue_libs/nonix-file-manager/services/NxFileManagerService.js`
   - Remove `downloadFile()`, `getFileUrl()`, `getPreviewUrl()`, `getStreamUrl()` methods
   - Keep only basic CRUD operations

### Frontend Components (7 files):
3. `vue_libs/nonix-file-manager/NxFileManager.vue`
4. `vue_libs/nonix-file-manager/components/NxFileListView.vue`
5. `vue_libs/nonix-file-manager/components/NxFilePreview.vue`
6. `vue_libs/nonix-file-manager/components/NxFilePreviewPane.vue`
7. `vue_libs/nonix-file-manager/components/NxFileTree.vue`
8. `vue_libs/nonix-file-manager/components/NxFileUploadField.vue`
9. `vue_libs/nonix-file-manager/components/NxFileUploadArea.vue`

**For each Vue component:**
   - Replace `<button @click="downloadFile(file)">` with `<a :href="file.url" download>`
   - Replace `<img :src="getPreviewUrl(file.id)">` with `<img :src="file.url">`
   - Replace `<video :src="getStreamUrl(file.id)">` with `<video :src="file.url">`
   - Remove component methods that call the removed service methods

**TOTAL: 9 files to modify completely documented**