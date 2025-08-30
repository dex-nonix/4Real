### LLM Tools – Plugin‑First Registry and UI Integration

#### Goal
- **Plugin‑first**: All LLM tools come from plugins via the in‑memory registry. No manual DB mapping is required for availability.
- **Persona access**: Controlled by wildcard patterns per persona (allow/deny) against the registry.
- **Hybrid (optional)**: Keep `internal_tools` only for metadata overrides or custom non‑plugin tools (e.g., `module.function`).
- **UI**: A single component named `LlmTool` used in edit/display modes under type key `llm_tool`.

---

### Backend changes (registry‑driven)

1) Expose registry listing (read‑only) via Chat service
- **Add route to Chat service (or ToolExecutionMixin)**
- **Endpoint**: `GET /chat/tools/registry`
  - Returns all registered tools from `AgenticToolManager.list()` as:
  - `{ "data": [{ "name": "namespace:tool_name", "description": "..." }] }`
  - Description source: plugin tuple third item; fallback to function `__doc__`; fallback to `Execute <name>`

2) Persona access resolution (drop DB gating for availability)
- **Edit file**: `faster_backend/nonix_web_agentic/llm/agentic_tool_manager.py`
- **Change**: Build persona tool map from the in‑memory registry only (no `InternalTool` filter):
  - Load persona (for potential `artist_id` pre‑binding as today)
  - Load `PersonaToolAccess` patterns for the persona (both `allow == True` and `allow == False`)
  - Evaluate access:
    - If any deny pattern matches → exclude
    - Else if any allow pattern matches → include
    - Else → exclude (default deny)
  - Preserve existing partial pre‑binding for first parameter `artist_id` when persona has `artist_id`
- **Apply same logic** to:
  - `build_persona_tool_map(persona_id)`
  - `list_persona_tools(persona_id)` (and keep signature analysis and `artist_id` masking as now)

3) Optional hybrid support (keep DB only for overrides/custom)
- **File (existing)**: `faster_backend/nonix_web_agentic/models/internal_tool.py`
- **Purpose**:
  - Optional metadata override: `description`, `config_json` per tool
  - Optional custom tool definitions: allow specifying `module.function` for runtime import and registration
- **Note**: Availability must not depend on this table. Treat presence as an override only.

---

### Frontend changes (dynamic form widgets)

1) New component (single name, two modes)
- **Create file**: `vue_libs/nonix/dynamic-form/widgets/LlmTool.vue`
- **Component name**: `LlmTool`
- **Type key**: `llm_tool`
- **Props**:
  - `modelValue: string`
  - `mode: 'edit' | 'display'` (default `'edit'`)
  - `allowWildcards: boolean` (default `true`)
  - `placeholder?: string`
  - `fetchUrl?: string` (default `'/chat/tools/registry'`)
- **Events**: `update:modelValue(string)`, `change(string)`
- **Behavior**:
  - Edit mode: free‑text input with autocomplete suggestions loaded from the registry; selecting a suggestion sets the exact qualified name; wildcards (`namespace:*`) fully allowed
  - Display mode: readonly value (chip/monospace) with optional tooltip from description
  - Caching: cache registry list in memory; debounce fetch; render as plain text if fetch fails

2) Register widgets in Nonix registries
- **Edit file**: `vue_libs/nonix/registries/edit-widgets.js`
  - Register: `EDIT_WIDGETS['llm_tool'] = { component: LlmTool, defaultProps: { allowWildcards: true, placeholder: 'Select or type a tool' } }`
  - Import path: `import LlmTool from '@nonix/dynamic-form/widgets/LlmTool.vue'`
- **Edit file**: `vue_libs/nonix/registries/display-widgets.js`
  - Register: `DISPLAY_WIDGETS['llm_tool'] = { component: LlmTool, defaultProps: { mode: 'display' } }`
  - Import path: `import LlmTool from '@nonix/dynamic-form/widgets/LlmTool.vue'`

3) Use in CRUD configs
- **File**: `src/services/PersonaToolAccessService.js`
  - Form field: change `pattern` to use the new type
    - `{ key: 'pattern', type: 'llm_tool', label: 'Tool', required: true, props: { allowWildcards: true } }`
  - Table column: optional display via `type: 'llm_tool'`
- **Note**: Keep free‑text to support wildcards and custom `module.function` values.

---

### API contract
- **GET** `/chat/tools/registry`
- **200 OK** body:
```
{ "data": [ { "name": "namespace:tool_name", "description": "..." } ] }
```
- **Notes**:
  - Stable `name` equals the qualified name used during plugin registration
  - `description` best‑effort: plugin tuple → function docstring → `Execute <name>`

---

### Implementation checklist
Backend
- [ ] Add `GET /chat/tools/registry` route inside Chat service (or ToolExecutionMixin)
- [ ] Update `build_persona_tool_map` to use registry + allow/deny patterns (no `InternalTool` gating)
- [ ] Update `list_persona_tools` with the same logic and keep signature extraction

Frontend
- [ ] Create `vue_libs/nonix/dynamic-form/widgets/LlmTool.vue`
- [ ] Register `llm_tool` in `edit-widgets.js` and `display-widgets.js`
- [ ] Switch `pattern` field in `src/services/PersonaToolAccessService.js` to `type: 'llm_tool'`

Validation
- [ ] With only plugin tools and a persona allow pattern (e.g., `music:*`), the selector lists tools; wildcard typing still works
- [ ] Deny pattern (e.g., `music:dangerous_tool`) hides or blocks that specific tool even if `music:*` is allowed
- [ ] Execution via tool‑call works without any `internal_tools` rows

---

### Notes for hybrid usage (optional)
- To define a custom tool not coming from any plugin, use `internal_tools` as metadata and implement a one‑time runtime import/registration based on `qualified_name` mapping to `module.function`.
- Overriding descriptions/config: if an override exists in `internal_tools`, prefer it in the display; otherwise use the registry description.


