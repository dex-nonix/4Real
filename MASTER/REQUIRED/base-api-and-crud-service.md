## BaseApiService.js and CrudService.js (Frontend)

Goal: Prime-first, minimal, fetch-based services that mirror the backend CRUD API. No custom frameworks. Clean, reusable, predictable.

Environment-aware base URL
- Use `VITE_API_BASE_URL` to point to the backend host + `/api`.
- Examples:
  - Dev (with Vite proxy): `VITE_API_BASE_URL=/api`
  - Prod: `VITE_API_BASE_URL=https://backend-host:5000/api`
- `BaseApiService` reads the base URL from the environment internally. No baseURL is passed by callers.
- `CrudService` builds endpoints RELATIVE to this base (e.g., `/${entity}`, `/${entity}/{id}`), so you never prefix `/api` twice.

### Files
- `src/services/BaseApiService.js`
- `src/services/CrudService.js` (extends `BaseApiService`)

### Design Principles
- Single responsibility, small surface area
- Native `fetch` under the hood (no extra libs)
- Sensible defaults, configurable per entity
- Unified error shape; consistent JSON handling
- Works with `CrudManager`, `DynamicTable`, `DynamicForm`

---

## BaseApiService (abstract)

Purpose: Provide a thin, safe HTTP layer with JSON handling, query params, and optional hooks for auth/logging.

Constructor
- `new BaseApiService(options)`
  - `options.defaultHeaders?: Record<string,string>` (e.g., `{ 'Content-Type':'application/json' }`)
  - `options.onRequest?: (req) => void | Promise<void>`
  - `options.onResponse?: (res) => void | Promise<void>`
  - `options.onError?: (error) => void | Promise<void>`
  - `options.fetchImpl?: typeof fetch`
  - Note: Base URL is sourced from `VITE_API_BASE_URL` internally.

Public Methods
- `setAuthToken(token: string | null)`
  - Stores a bearer token internally; when set, adds `Authorization: Bearer <token>` to requests
- `buildUrl(path: string, query?: Record<string, any>): string`
  - Concatenates environment-based API_BASE_URL + path, encodes `query` as `?key=value` (skips null/undefined)
- `request(method: 'GET'|'POST'|'PUT'|'PATCH'|'DELETE', path: string, options?: { query?, body?, headers?, signal? })`
  - JSON encodes `body` (when provided and not `FormData`)
  - Merges headers with defaults and auth
  - Calls hooks (`onRequest`, `onResponse`, `onError`)
  - Parses JSON responses automatically when `Content-Type` is JSON
  - Returns `{ status, ok, data, headers }`
  - Throws an error object `{ status, message, data }` on non-OK
- Convenience methods
  - `get(path, options?)`
  - `post(path, options?)`
  - `put(path, options?)`
  - `patch(path, options?)`
  - `delete(path, options?)`

Path Scoping
- `basePath(): string` — subclasses override to return their base scope (e.g., `'/artists'`)
- All requests are automatically scoped to `basePath()`:
  - Passing `'/'` targets `basePath()` itself
  - Passing `'/id'` becomes `basePath() + '/id'`
  - Passing `'search'` becomes `basePath() + '/search'`
  - Passing an empty string or `undefined` behaves like `'/'`

Notes
- Timeouts can be implemented by callers via `AbortController` and passing `signal`
- No retry by default (keep minimal)

---

## CrudService (abstract, extends BaseApiService)

Purpose: Generic CRUD wrapper tied to an entity; mirrors backend routes exactly. The service HOLDS the CRUD UI config passed via the constructor. No endpoint overrides.

Constructor
- `new CrudService(entity: string, uiConfig: { table: any, form: any })`
  - `entity`: backend route name (e.g., `'artists'`, `'rhyme-techniques'`)
  - `uiConfig`: UI configuration object for CrudManager (table + form), passed via the base constructor and stored on `this.config`

Public Methods (all paths are relative; BaseApiService scopes them to `/${entity}` via `basePath()`)
- `list(params?: { q?, page?, per_page?, sort?, order?, ...extra })`
  - GET `'/'` (scoped to `/${entity}`) with `params`; returns `{ data, pagination? }`
- `get(id: string | number)`
  - GET `'/'+id` (scoped to `/${entity}/{id}`); returns `{ data }`
- `create(payload: Record<string, any>)`
  - POST `'/'` (scoped to `/${entity}`) with JSON body; returns `{ data }`
- `update(id: string | number, payload: Record<string, any>)`
  - PUT `'/'+id` (scoped to `/${entity}/{id}`) with JSON body; returns `{ data }`
- `delete(id: string | number)`
  - DELETE `'/'+id` (scoped to `/${entity}/{id}`); returns `{ message }`
- `search(params?: Record<string, any>)`
  - GET `'/search'` (scoped to `/${entity}/search`) with `params`; returns `{ data, pagination? }`
- `bulk(operation: 'delete' | 'update', payload: Record<string, any>)`
  - POST `'/bulk'` (scoped to `/${entity}/bulk`) with `{ operation, ...payload }`; returns `{ message }`
- `bulkDelete(ids: Array<string | number>)`
  - Convenience for `bulk('delete', { ids })`
- `selectorList(params?: Record<string, any>)`
  - GET `'/selector'` (scoped to `/${entity}/selector`); returns `{ data }`
- `selectorGet(id: string | number)`
  - GET `'/selector/'+id` (scoped to `/${entity}/selector/{id}`); returns `{ data }`

Defaults (auto-merged into `config.table` unless overridden)
- `actions`: `['view', 'edit', 'delete']`
- `bulkActions`: `['delete', 'export']`
- `paginated`: `true`
- `pageSize`: `20`
- `selectionMode`: `'multiple'`
- `resizable`: `true`
- `striped`: `true`
- `hover`: `true`

Notes
- Pass-through query params let `DynamicTable` control search/pagination/sorting
- Keep response shape unchanged; presentation components decide how to consume

Param Naming (match backend exactly)
- Pagination: `page` (1-based), `per_page`
- Sorting: `sort`, `order` where order is `asc` or `desc`
- Filters: send as `filter_<field>=<operator>:<value>` (e.g., `filter_name=like:John`, `filter_genre=in:rock,pop`)

Examples
```js
// List page 2, 20 per page, sorted by name desc, filter status=active
await service.list({ page: 2, per_page: 20, sort: 'name', order: 'desc', filter_status: 'eq:active' })

// Search title and genre fields
await service.search({ q: 'met', fields: 'title,genre', page: 1, per_page: 20 })

// Bulk delete
await service.bulkDelete([1, 2, 3])

// Selector list for dropdown
await service.selectorList({ q: 'met' })
```

---

## Usage Patterns

Per-entity service subclasses (recommended)
```js
// src/services/ArtistService.js
import CrudService from './CrudService'

export default class ArtistService extends CrudService {
  constructor() {
    super('artists', {
      table: {
        columns: [
          { field: 'name', header: 'Artist Name', type: 'text', sortable: true },
          { field: 'abbreviation', header: 'Abbr', type: 'text', sortable: true }
        ],
        filters: ['search', 'date_range'],
      },
      form: {
        fields: [
          { key: 'name', type: 'text', label: 'Artist Name', required: true, props: { placeholder: 'Enter artist name' } },
          { key: 'abbreviation', type: 'text', label: 'Abbreviation', required: true, props: { placeholder: 'Enter abbreviation' } }
        ]
      }
    })
  }
}

// Create a singleton instance and export it, or instantiate where used
// export const artistService = new ArtistService()
```

With CrudManager (service instance only; no globals)
- CrudManager receives a single prop: `service` (instance of a CrudService subclass)
- It reads UI from `service.config.table` and `service.config.form`
- It calls backend via `service.list/create/update/delete/bulkDelete`

---

## Error Handling Contract
- On non-OK responses, throw `{ status, message, data }`
- `message` should be derived from backend payload (`data.message || data.error || statusText`)
- Components (CrudManager) catch and surface via PrimeVue ToastService

## Auth Handling (optional)
- `setAuthToken(token)` to enable `Authorization: Bearer` header
- Or provide an `onRequest` hook to inject headers dynamically

## Testing
- Allow injecting a custom `fetchImpl` in `BaseApiService` options for tests/mocks
- Keep no side effects; services are plain instances

## Type Hints (JSDoc)
- Use JSDoc on all public methods for editor IntelliSense
- Keep types generic to avoid tight coupling

---

## Minimal Example (pseudocode)
```js
// Service subclass and instance
import ArtistService from '@/services/ArtistService'
const artistService = new ArtistService()

// In CrudManager
await artistService.list({ q: search, page, per_page: pageSize })
await artistService.create(formData)
await artistService.update(id, formData)
await artistService.delete(id)
await artistService.bulkDelete(selectedIds)
```

This spec mirrors the backend CRUD routes and provides a simple, Prime-first way to wire UI actions to API endpoints without extra libraries or custom CSS.

