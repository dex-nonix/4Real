## BaseApiService.js and CrudService.js (Frontend)

Goal: Prime-first, minimal, fetch-based services that mirror the backend CRUD API. No custom frameworks. Clean, reusable, predictable.

Environment-aware base URL
- Use `VITE_API_BASE_URL` to point to the backend host + `/api`.
- Examples:
  - Dev (with Vite proxy): `VITE_API_BASE_URL=/api`
  - Prod: `VITE_API_BASE_URL=https://backend-host:5000/api`
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
  - `options.baseURL: string` (required)
  - `options.defaultHeaders?: Record<string,string>` (e.g., `{ 'Content-Type':'application/json' }`)
  - `options.onRequest?: (req) => void | Promise<void>`
  - `options.onResponse?: (res) => void | Promise<void>`
  - `options.onError?: (error) => void | Promise<void>`

Public Methods
- `setAuthToken(token: string | null)`
  - Stores a bearer token internally; when set, adds `Authorization: Bearer <token>` to requests
- `buildUrl(path: string, query?: Record<string, any>): string`
  - Concatenates `baseURL + path`, encodes `query` as `?key=value` (skips null/undefined)
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

Notes
- Timeouts can be implemented by callers via `AbortController` and passing `signal`
- No retry by default (keep minimal)

---

## CrudService (abstract, extends BaseApiService)

Purpose: Generic CRUD wrapper tied to an entity or explicit endpoints; mirrors backend `CrudService` routes.

Constructor
- `new CrudService(options)`
  - `options.baseURL: string` (required)
  - `options.entity?: string` e.g., `'artists'`
  - `options.endpoints?: { list?, get?, create?, update?, delete?, bulkDelete? }`
    - Defaults when `entity` is provided:
      - `list: `/${entity}` (GET)`
      - `get: `/${entity}/{id}` (GET)`
      - `create: `/${entity}` (POST)`
      - `update: `/${entity}/{id}` (PUT)`
      - `delete: `/${entity}/{id}` (DELETE)`
      - `bulkDelete: `/${entity}/bulk-delete` (POST)`

Public Methods
- `list(params?: { q?, page?, per_page?, sort?, order?, ...extra })`
  - GET `endpoints.list` with `params` as query string
  - Returns `Array<any>` or `{ items, total }` depending on backend. Consumers should handle both; this service returns `data` as received.
- `get(id: string | number)`
  - GET `endpoints.get` replacing `{id}`
- `create(payload: Record<string, any>)`
  - POST `endpoints.create` with JSON body
- `update(id: string | number, payload: Record<string, any>)`
  - PUT `endpoints.update` replacing `{id}` with JSON body
- `delete(id: string | number)`
  - DELETE `endpoints.delete` replacing `{id}`
- `bulkDelete(ids: Array<string | number>)`
  - POST `endpoints.bulkDelete` with `{ ids }`

Helpers
- `resolveEndpoint(template: string, vars: Record<string,string|number>)`
  - Replaces `{id}` etc. in templates

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
await service.bulk({ operation: 'delete', ids: [1,2,3] })

// Selector list for dropdown
await service.selectorList({ q: 'met' })
```

---

## Usage Patterns

Singleton services per entity (recommended)
```js
// src/services/ArtistService.js
import CrudService from './CrudService'
export const artistService = new CrudService({ baseURL: import.meta.env.VITE_API_BASE_URL, entity: 'artists' })
```

Injection as a plugin (optional)
- Create a small plugin that registers a map of entity services and injects `$api`
- Example: `app.config.globalProperties.$api = { artist: artistService, album: albumService, ... }`
- Alternatively, inject a factory: `getCrudService(entity)` → returns a memoized `CrudService`

With CrudManager
- CrudManager receives a `config` with:
  - `entity: string`
  - `api.endpoints?: overrides`
  - `table: DynamicTable config`
  - `form: { fields: FieldItem[] }`
- CrudManager uses the corresponding `CrudService` to call `list/create/update/delete/bulkDelete`

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
// Bootstrapping
import CrudService from '@/services/CrudService'
export const artistService = new CrudService({ baseURL: import.meta.env.VITE_API_BASE_URL, entity: 'artists' })

// In CrudManager
await artistService.list({ q: search, page, per_page: pageSize })
await artistService.create(formData)
await artistService.update(id, formData)
await artistService.delete(id)
await artistService.bulkDelete(selectedIds)
```

This spec mirrors the backend CRUD routes and provides a simple, Prime-first way to wire UI actions to API endpoints without extra libraries or custom CSS.

