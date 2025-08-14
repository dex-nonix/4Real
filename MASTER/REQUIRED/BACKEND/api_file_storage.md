### Backend: File Storage and Media Linking

This document defines a simple, professional file storage subsystem (two core tables) and a generic linking mechanism to attach files to any entity (e.g., Tracks, Albums, Artists), with runtime-usable CRUD, selectors, previews, and an upload endpoint.

---

## Goals

- **Simple core storage**: exactly two tables for storage itself: `file_categories`, `files`.
- **Generic linking**: one small link table `file_links` to attach any `files.id` to any entity `(<entity_type>, <entity_id>)` with `status` and `comment`.
- **CRUD-first**: one service per table using the existing `CrudService` with selectors and filters.
- **Upload**: a single multipart upload endpoint in `FileService` writing to `uploads/` in dev, returning a `files` row.
- **Previews**: lightweight preview for images/audio in table display; FK selectors for form fields.
- **DB/runtime-managed**: everything configurable via DB + UI; no env fallbacks for core behavior.

---

## Data Models (SQLAlchemy)

Note: Field names align with existing conventions; timestamps use `server_default=func.now()`, `onupdate=func.now()`.

### FileCategory (`file_categories`)

- `id` (PK, int)
- `name` (str, required)
- `slug` (str, unique, optional)
- `description` (text, optional)
- `created_at` (datetime)
- `updated_at` (datetime)

Selector label: `name`.

### File (`files`)

- `id` (PK, int)
- `category_id` (FK → `file_categories.id`, nullable)
- `title` (str, optional) — human label; fallback to `original_filename`
- `original_filename` (str, required)
- `mime_type` (str, required)
- `size_bytes` (int, required)
- `storage_url` (str, required) — browser-accessible URL; dev: `/uploads/<filename>`
- `sha256` (str, optional) — duplicate detection (best-effort)
- `width` (int, optional) — for images
- `height` (int, optional) — for images
- `duration_seconds` (int, optional) — for audio/video
- `created_at` (datetime)
- `updated_at` (datetime)

Selector fields: `['title', 'original_filename']`; label: `title || original_filename`.

### FileLink (`file_links`) — generic attachment

- `id` (PK, int)
- `file_id` (FK → `files.id`, required)
- `entity_type` (str, required) — e.g., `'track'`, `'album'`, `'artist'`
- `entity_id` (int, required)
- `status` (enum/str, required) — `'prototype' | 'snippet' | 'final'` (allow additional values if needed)
- `comment` (text, optional)
- `sort_order` (int, optional, default 0)
- `created_at` (datetime)
- `updated_at` (datetime)

Indexes recommended: `(entity_type, entity_id)`, `(file_id)`.

---

## Services and Endpoints

All services are standard `CrudService` subclasses with full create/read/update/delete/list/search/bulk/selector support, plus one custom upload endpoint.

### FileCategoryService (`/api/file-categories`)

- Filters: `name`, `slug`
- Sorting: `name`
- Validation: `name` required, `slug` unique if provided
- Selector: fields `['name']`, label: `name`

### FileService (`/api/files`)

- Filters: `category_id`, `mime_type`, `title`, `original_filename`
- Sorting: `created_at` (client can request `order=desc` for newest-first)
- Validation: `original_filename`, `mime_type`, `size_bytes`, `storage_url`
- Selector: fields `['title', 'original_filename']`, label: `title || original_filename`

Custom upload endpoint (multipart):

- `POST /api/files/upload`
  - Form fields:
    - `file` (required) — the binary file
    - `title` (optional) — human label
    - `category_id` (optional) — FK
  - Behavior:
    - Saves the file to `uploads/` (dev) with a safe unique filename
    - Derives `mime_type`, `size_bytes`, computes `sha256` (optional)
    - Creates a `files` row and returns it
  - Response: `{ data: { ...files row... } }`

Dev static serving: expose `/uploads/<filename>` (read-only) for previews.

### FileLinkService (`/api/file-links`)

- Filters: `entity_type`, `entity_id`, `status`, `file_id`
- Sorting: `sort_order asc, created_at desc`
- Validation: `file_id`, `entity_type`, `entity_id`, `status`
- Selector: fields `[]` (link rows are not typically selected globally)

---

## Selector Behavior (for FK widgets)

- `FileCategoryService.selector` → label: `name`
- `FileService.selector` → label: `title || original_filename`
- `FileLinkService.selector` → not commonly used; consumers should select `files` then create a link

These enable frontend `fk_select` for `category_id` and `file_id` fields and `fk_display` in tables.

---

## Frontend Integration Notes

- Services:
  - `FileCategoryService.js` → entity key: `file-categories`
  - `FileService.js` → entity key: `files` (add `upload(file, { title, category_id })` using `FormData` → `POST /api/files/upload`)
  - `FileLinkService.js` → entity key: `file-links`

- Widgets:
  - `file_select` (edit): `fk_select` targeting `files` with search enabled
  - `file_preview` (display): renders thumbnail if `mime_type` starts with `image/`, `<audio controls>` if `audio/`, else an icon + filename
  - Optional `file_upload` widget: uploads via `FileService.upload(...)`, sets `file_id` on the form

- Track attachments UI (example):
  - On `Track` view/edit, embed a `CrudManager` for `file-links` with:
    - `fixedFilters`: `{ filter_entity_type: 'eq:track', filter_entity_id: 'eq:<trackId>' }`
    - Form fields: `file_id (file_select)`, `status (select: prototype/snippet/final)`, `comment (text)`, `sort_order (number)`
    - Table columns: `file (file_preview)`, `status`, `comment`, `sort_order`
  - Reuse the same pattern for `Album` / `Artist` by changing `fixedFilters`.

---

## Example API Usage

Upload a file (dev):

```bash
curl -X POST http://localhost:5173/api/files/upload \
  -F file=@/path/to/demo.mp3 \
  -F title="Demo snippet" \
  -F category_id=1
```

Create a link to a Track (track id 42):

```bash
curl -X POST http://localhost:5173/api/file-links/ \
  -H 'Content-Type: application/json' \
  -d '{
    "file_id": 10,
    "entity_type": "track",
    "entity_id": 42,
    "status": "snippet",
    "comment": "Rough cut"
  }'
```

---

## Acceptance Criteria

- Can create categories and upload files; previews load via `/uploads/...` in the UI.
- Can attach multiple files to any entity using `file-links` with `status` and `comment`.
- `fk_select` works for choosing files in forms; `file_preview` displays in tables.
- All endpoints follow the generic `CrudService` patterns and selector APIs.

---

## Implementation Checklist

- Models: `file_category.py`, `file.py`, `file_link.py`
- Services: `file_category_service.py`, `file_service.py` (with `/upload`), `file_link_service.py`
- App registration: import and register services in `backend/app/__init__.py`
- Static serving for `/uploads/` in dev (`config.py` path; Flask route in `backend/wsgi.py`)
- Frontend services: `FileCategoryService.js`, `FileService.js` (with `upload`), `FileLinkService.js`
- Widgets: register `file_select` (edit) and `file_preview` (display) with widget managers
- Track UI: embed `CrudManager` for `file-links` with fixed filters for current track

Status: Implemented. Tables and services added, `/api/files/upload` available, and dev static serving at `/uploads/<filename>`.

Runtime config (dev):

- `UPLOAD_DIR` (default: `backend/app/uploads`)
- `MAX_CONTENT_LENGTH` (default: `50MB`)


