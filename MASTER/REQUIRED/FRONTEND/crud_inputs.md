## CRUD Inputs (Frontend) — Complete Guide

This document explains the input widgets used by CRUD forms, including how to add Foreign-Key (FK) selectors that talk to the backend selector endpoints. It assumes no prior knowledge.

### What you already have
- A generic CRUD form renderer: `src/components/forms/DynamicForm.vue`
- A widget manager: `src/widgets/edit-widgets.js` (PrimeVue components already registered: text, select, date, etc.)
- Backend selector API for any entity (provided by CrudService):
  - GET `/api/{entity}/selector?q=...` (list/search options)
  - GET `/api/{entity}/selector/{id}` (resolve label for a specific id)
- Frontend service helpers in `CrudService.js`:
  - `selectorList(params)` → GET `/${entity}/selector`
  - `selectorGet(id)` → GET `/${entity}/selector/${id}`

---

## 1) Basic input types (existing)

Use these for simple scalar fields:
- text: single-line string input
- textarea: multi-line text
- number: numeric input
- date: date picker
- select: static option dropdown
- multi_select: static multi-option dropdown
- json: PrimeVue editor, used for `*_json` fields

DynamicForm field item (simplified):
```json
{
  "key": "name",
  "type": "text",
  "label": "Name",
  "required": true,
  "props": { "placeholder": "Enter name" }
}
```

---

## 2) Foreign-Key (FK) widgets (to implement)

Purpose: select related entities using the backend selector endpoints. These widgets store only the numeric ID(s), but display labels fetched from the backend.

### 2.1 fk_select (single ID dropdown)
- Use when the option set is modest or you want a searchable dropdown.
- v-model: `number` (the ID)
- Props:
  - `entity` (string, required) — e.g., `'personas'`, `'mcp-servers'`
  - `valueKey` (string, default `'id'`) — the value field from selector API
  - `labelKey` (string, default `'label'`) — the display label
  - `placeholder` (string)
  - `clearable` (boolean)
  - `disabled` (boolean)
  - `search` (boolean, default false) — when true, call selector with `q`
  - `debounceMs` (number, default 250)
  - `params` (object) — extra query params for selectorList (e.g. `{ limit: 50 }`)
  - `resolveOnMount` (boolean, default true) — call selectorGet for initial id

Behavior:
- On mount: if `modelValue` present and `resolveOnMount`, call `selectorGet(id)` and show label.
- Dropdown opens with cached options; search calls `selectorList({ q })` debounced.

Example (form field):
```json
{ "key": "persona_id", "type": "fk_select", "label": "Persona", "required": true, "props": { "entity": "personas", "search": true } }
```

### 2.2 fk_autocomplete (single ID with remote search)
- Use for large datasets; always searches the backend.
- v-model: `number` (the ID)
- Props: same as `fk_select`, but behaves like an autocomplete (no big preloaded list).

### 2.3 fk_multi_select (multiple IDs)
- Use for M:N relations.
- v-model: `number[]` (array of IDs)
- Props: same as `fk_select`, but `multiple` selection.

### 2.4 fk_display (read-only label renderer)
- Use in tables or in DynamicForm display mode to show labels instead of IDs.
- Props:
  - `entity` (string, required)
  - `valueKey`/`labelKey` (same defaults as above)
  - `resolveOnMount` (boolean, default true)
- Behavior: given an ID or array of IDs, fetch labels via `selectorGet`. Cache results to avoid repeated calls.

Example (table column):
```json
{ "field": "persona_id", "header": "Persona", "type": "fk_display", "props": { "entity": "personas" } }
```

---

## 3) Using FK widgets in CRUD forms

Typical cases:
- PersonaMCPServer form:
```json
{
  "key": "persona_id", "type": "fk_select", "label": "Persona", "required": true,
  "props": { "entity": "personas", "search": true }
},
{
  "key": "mcp_server_id", "type": "fk_select", "label": "MCP Server", "required": true,
  "props": { "entity": "mcp-servers", "search": true }
}
```

- M:N field in a Track form (styles):
```json
{ "key": "style_ids", "type": "fk_multi_select", "label": "Styles", "props": { "entity": "styles" } }
```

DynamicForm passes the `props` down to the widget. The widget internally calls `/selector` endpoints through the entity service.

---

### 3.1 File selection and attachments (new)

- To select an uploaded file: use `fk_select` with `entity: 'files'`.
- To attach files to a `Track` (or any entity), use the generic `file-links` CRUD with fixed filters:

Form fields for `file-links`:
```json
[
  { "key": "file_id", "type": "fk_select", "label": "File", "required": true, "props": { "entity": "files", "search": true } },
  { "key": "status", "type": "select", "label": "Status", "required": true, "props": { "options": ["prototype","snippet","final"] } },
  { "key": "comment", "type": "text", "label": "Comment" },
  { "key": "sort_order", "type": "number", "label": "Order" }
]
```

Table columns for `file-links`:
```json
[
  { "field": "file_id", "header": "File", "type": "fk_display", "props": { "entity": "files" } },
  { "field": "status", "header": "Status", "type": "text" },
  { "field": "comment", "header": "Comment", "type": "text" },
  { "field": "sort_order", "header": "Order", "type": "number" }
]
```

Embed in a Track page using fixed filters:
```js
// CrudPage meta example
{
  key: 'file-links',
  fixedFilters: { filter_entity_type: 'eq:track', filter_entity_id: `eq:${trackId}` }
}
```

---

## 4) Backend selector API (how it formats options)

Selector responses (already implemented by CrudService):
- List (GET `/selector`):
```json
{
  "data": [
    { "id": 1, "value": 1, "label": "John Doe" }
  ],
  "total": 1
}
```
- Single (GET `/selector/{id}`):
```json
{ "data": { "id": 1, "value": 1, "label": "John Doe" } }
```

Notes:
- The exact label is controlled by each service’s `selector` config (`fields`, `display_format`, `search_fields`, `limit`, `order_by`).
- ID is always provided; label is consistent for the entity.

---

## 5) Implementation details (frontend)

Where to add code:
- `src/widgets/edit-widgets.js`: register three new edit widgets: `'fk_select'`, `'fk_autocomplete'`, `'fk_multi_select'`.
- `src/widgets/display-widgets.js` (or table display manager): register `'fk_display'`.

How to resolve options:
- Prefer using injected service if available (e.g., `inject('personas')`), else create a `new CrudService(entity)` dynamically to call `selectorList/selectorGet`.
- Cache results per entity (and per search term) to minimize requests.
- Debounce search; cancel previous in-flight calls on new input.

Validation:
- DynamicForm already handles `required`. If a field is `required: true`, the widget must emit a valid ID/IDs for the form to submit.

Display Mode:
- When `mode='display'`, DynamicForm uses the display manager. Set field `type: 'fk_display'` (or set `displayWidget` explicitly) to render the human-readable label.

Accessibility:
- Ensure widgets expose labels via `aria-label` or associate labels by `for/id` as DynamicForm already does.
- For searchable inputs, announce “n results” as needed or rely on PrimeVue’s built-in announcements.

---

## 6) Quick checklist

1) Register FK edit widgets in `edit-widgets.js` and FK display widget in the display manager.
2) Implement option loading via `selectorList/selectorGet` and enable search with debounce.
3) Add form config entries for FK fields (`persona_id`, `mcp_server_id`, etc.).
4) Add table column configs with `fk_display` for FK columns.
5) Test: open Persona MCP Servers and verify dropdowns show labels; save and ensure IDs post to backend.

This completes CRUD-backed selection inputs for all FK fields.


