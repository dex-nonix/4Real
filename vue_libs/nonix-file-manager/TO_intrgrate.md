# FILE MANAGER API ISSUES & SOLUTIONS

## ⚠️ CRITICAL: APPROACH CLARIFICATION

**PRIMARY SOLUTION:** Backend provides absolute full URLs in `url` field. Frontend uses them directly with NO URL construction.

**NOT THE SOLUTION:** Fixing `buildUrl()` or `basePath` to construct URLs in frontend.

**WHY:** Normal web development - backend delivers complete URLs, frontend consumes directly like `<img src="file.url">`.

---

## PROBLEM 1: BACKEND DOESN'T PROVIDE FULL URLs

**Current:** Backend returns `storage_url: "/static/uploads/file.jpg"` (relative path)
**Required:** Backend returns `url: "https://server.com/api/file-manager/files/123"` (absolute full URL)

### IMPACT:
- Frontend cannot use files directly in HTML
- Requires complex URL construction logic
- Not normal web development behavior

## PROBLEM 2: DOWNLOAD URL ISSUE

**Users get `/api/files/1/download` instead of `/api/file-manager/files/1/download`**

### ROOT CAUSE:
- `NxFileManagerService.basePath = () => '/file-manager'` fails at runtime
- `basePath()` returns empty string instead of `'/file-manager'`
- URL becomes `/api/files/1/download` (wrong router) instead of `/api/file-manager/files/1/download`

### WHY IT HAPPENS:
- `basePath()` works for async `request()` calls (listFiles, deleteFile)
- `basePath()` fails for direct `buildUrl()` calls (downloadFile)
- Timing or context issue in direct URL construction

### CURRENT IMPACT:
- Download requests hit `FileRouter` (no download endpoint) → 404
- Should hit `FileManagerRouter` (has download endpoint) → 200

## API OVERCOMPLEXITY ISSUES

### PROBLEM 1: TOO MANY SIMILAR METHODS
```javascript
// ❌ Current complex API
async downloadFile(fileId) {
  const url = this.buildUrl(`/files/${fileId}/download`)
  window.open(url, '_blank') // UI logic in service!
}

async getFileUrl(fileId, action = 'preview') {
  return this.buildUrl(`/files/${fileId}/${action}`)
}

async getPreviewUrl(fileId) {
  return this.getFileUrl(fileId, 'preview') // Unnecessary wrapper
}
```

### PROBLEM 2: BACKEND HAS UNNECESSARY ENDPOINTS
- `/api/file-manager/files/{id}/download`
- `/api/file-manager/files/{id}/preview` 
- `/api/file-manager/files/{id}/stream`

### PROBLEM 3: MIXED CONCERNS
- Service layer contains UI logic (`window.open()`)
- Frontend handles complex download logic with blobs
- Action parameters complicate simple file access

## SOLUTION: BACKEND PROVIDES FULL URLs

### PRIMARY SOLUTION:
**Backend MUST include `url` field with absolute full URLs in ALL responses:**

```json
{
  "id": 123,
  "title": "My File",
  "filename": "file.jpg",
  "size": 1024000,
  "url": "https://server.com/api/file-manager/files/123"  // ✅ ABSOLUTE FULL URL
}
```

### FRONTEND USAGE (NO URL CONSTRUCTION):
```html
<!-- Normal HTML - uses backend-provided URLs directly -->
<a :href="file.url" download>Download</a>
<img :src="file.url" alt="Preview" />
<video :src="file.url" controls></video>
```

**NO `buildUrl()` calls, NO basePath logic, NO URL construction in frontend - just direct usage of backend-provided URLs.**

## BACKEND MUST **PERMANENTLY** DELIVER FULL URL

### BACKEND RESPONSE MUST INCLUDE `url` FIELD WITH FULL URL:
```json
{
  "id": 123,
  "title": "My File",
  "filename": "file.jpg",
  "size": 1024000,
  "url": "https://dev.local/api/file-manager/files/123"  // ✅ FULL URL - not relative!
}
```

### FOR EXTERNAL FILES:
```json
{
  "id": 456,
  "title": "External File",
  "filename": "external.jpg",
  "url": "https://cdn.example.com/files/external.jpg"  // ✅ FULL EXTERNAL URL
}
```

### CURRENT PROBLEM:
Backend currently returns:
```json
{
  "storage_url": "/static/uploads/file.jpg"  // ❌ RELATIVE - not usable directly
}
```

### REQUIREMENT:
- Backend MUST provide `url` field with complete, usable URL
- Frontend uses URL directly without construction
- Supports internal (`https://server.com/api/file-manager/files/123`) and external (`https://cdn.com/file.jpg`) URLs
- **PERMANENT REQUIREMENT** - no relative URLs or partial paths

### ONE ENDPOINT SERVES FILES:
```python
@router("/files/{file_id}")
async def get_file(file_id: int):
    # Get file and return with appropriate headers
    return FileResponse(path=file_path, filename=filename)
```

## SOLUTION SUMMARY

**ONLY ONE SOLUTION:** Backend provides `url` field with absolute full URLs in ALL file responses.

**NO URL CONSTRUCTION IN FRONTEND** - Frontend uses `file.url` directly in HTML like normal websites.

**RESULT:** Normal website file serving - backend delivers ready URLs, frontend consumes directly.

## RESULT: NORMAL WEBSITE FILE SERVING

- Backend serves files straightforwardly
- Frontend gets direct URLs in data
- No API complexity, no JavaScript tricks
- Works like any standard website
- Supports internal and external files seamlessly
