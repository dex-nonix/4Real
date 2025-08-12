## Integration Plan — Music Metadata Management System

### Guiding principles
- Minimal invention; prefer established libs and defaults
- Flask + SQLAlchemy + Flask-SQLAlchemy paginate
- Consistent JSON envelopes; predictable error format
- DRY, config-driven CRUD on both backend and frontend

### Locked decisions
- Backend ORM: SQLAlchemy via Flask-SQLAlchemy
- Pagination: Flask-SQLAlchemy `Query.paginate(page, per_page, error_out=False)`
- Response envelope: always `{ data, pagination? }` for lists/search; `{ data }` for single; `{ message }` for destructive success; `{ errors|error }` for failures
- Bulk ops endpoint: `POST /api/<entity>/bulk` with body `{ operation: 'delete'|'update', ids: number[], data?: object }`
- Selector endpoints: `GET /api/<entity>/selector` and `GET /api/<entity>/selector/{id}` with `{ data: [...] }` / `{ data: {...} }`
- CORS: enabled (all origins in dev)
- Auth: none for MVP (add later)
- DB: start with SQLite for fastest bring-up (`backend/app.db`), keep models portable to Postgres

### Phase 0 — Project scaffolding (done when both apps run)
- Backend directories: `backend/app/{__init__.py, decorators.py, services/{api_router.py, crud_service.py, artist_service.py}, models/{__init__.py, artist.py}}`, plus `backend/config.py`, `backend/requirements.txt`
- Frontend directories: `frontend/` Vue 3 app with PrimeVue, `src/components/{forms, tables, crud}`, `src/configs/crud/artist.js`, router/view `Artists.vue`

### Backend — Step-by-step
1) App and configuration
   - Create Flask app factory (`create_app`)
   - Configure SQLAlchemy URI (SQLite default), JSON, CORS
   - Register `APIRouter` blueprint at `/api`

2) Infrastructure
   - `decorators.expose(path, methods=['GET'])` as spec’d
   - `services/APIRouter`: discover exposed methods, register routes under `/api/<service>/<path>`
   - `services/CrudService`: implement all handlers per spec (create, list, read, update, delete, search, bulk, selector)
   - List/paginate: use `Query.paginate`; return `{ data, pagination }`

3) Model v0
   - `Artist`: `id`, `name` (unique, required), `abbreviation`, `persona` (Text), `birth_date` (Date), timestamps (`created_at`, `updated_at`)
   - `to_dict()` for serialization (or generic serializer)

4) Service v0
   - `ArtistService(CrudService)` with config:
     - `path: '/artists'`
     - filters: `name, abbreviation`
     - sorting default: `name`
     - validation: required `name`, unique `name`
     - selector: fields `[id, name, abbreviation]`, order `name`
   - Register with `APIRouter` as `artists`

5) DB lifecycle
   - For MVP: create tables on startup if not exist
   - Optional next: Flask-Migrate

### Frontend — Step-by-step
1) App and libraries
   - Vue 3 + PrimeVue + PrimeIcons + ToastService + Vue Router
   - Axios-based `BaseApiService` (`this.$api`) with base URL `/`

2) Components (minimal)
   - `components/crud/CrudManager.vue`: from spec, adjusted to consume envelopes:
     - list: use `resp.data.data` for rows, `resp.data.pagination` for paging
     - create/update/delete/bulk: map to endpoints
   - `components/forms/DynamicForm.vue`: minimal generator (text, date)
   - `components/tables/DynamicTable.vue`: minimal PrimeVue `DataTable` with columns, actions, pagination UI

3) Config
   - `configs/crud/artist.js` aligned to backend endpoints:
     - list: `/api/artists`
     - create: `/api/artists`
     - update: `/api/artists/{id}`
     - delete: `/api/artists/{id}`
     - bulk: `/api/artists/bulk`

4) View
   - `views/Artists.vue` renders `<CrudManager :config="artistCrudConfig" />`

### API contracts (MVP)
- POST `/api/artists` → 201 `{ message, data }`
- GET `/api/artists` (page, per_page, sort, order, filter_*) → 200 `{ data: [...], pagination: {...} }`
- GET `/api/artists/{id}` → 200 `{ data }` | 404 `{ error }`
- PUT `/api/artists/{id}` → 200 `{ message, data }` | 404 `{ error }`
- DELETE `/api/artists/{id}` → 200 `{ message }` | 404 `{ error }`
- GET `/api/artists/search?q=&fields=` → 200 `{ data, pagination? }`
- POST `/api/artists/bulk` body `{ operation: 'delete'|'update', ids: [], data? }` → 200 `{ message }`
- GET `/api/artists/selector?q=` → 200 `{ data: [{ id, value, label, ... }] }`
- GET `/api/artists/selector/{id}` → 200 `{ data: { id, value, label, ... } }`

### Error and validation format
- 400 validation: `{ errors: ["field message", ...] }`
- 404 not found: `{ error: "Not found" }`
- 500 server: `{ error: "message" }`

### Commands (dev)
Backend
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
FLASK_APP=backend.app:create_app FLASK_ENV=development flask run --port 5000
```
Frontend
```bash
cd frontend
npm install
npm run dev
```

### Milestones and acceptance
M1 Backend up (Artist only)
- App boots, `/api/artists` CRUD works, pagination returns envelope
- Selector endpoints return expected shapes

M2 Frontend up (Artist CRUD)
- Table renders data from `{ data }`
- Create, edit, delete via dialogs with toasts
- Pagination UI wired to backend
- Bulk delete via `/bulk`

M3 Hardening
- Basic input validation surfaced in UI
- CORS configured
- Code lint passes; no runtime errors in console

### Risks and mitigations
- Envelope mismatch → enforced contract above, tests in M1/M2
- Overbuilding widgets → start with text/date only; add as needed
- SQLite quirks → keep models simple; migrate to Postgres later

### Next actions (immediately after plan)
1) Populate `backend/requirements.txt` and scaffold backend files
2) Implement `Artist` model and `ArtistService`; register routes
3) Scaffold Vue app; add `CrudManager`, `DynamicForm`, `DynamicTable` minimal
4) Wire `artistCrudConfig` and verify end-to-end

