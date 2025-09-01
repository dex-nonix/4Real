## Agentic Tools: Open Issues and Planned Fixes (No Fallbacks — Strict Alignment)

### Canonical Conventions (must be applied everywhere)
- Keys: snake_case across DB, backend payloads, WebSocket events, and UI.
- Dates: canonical ISO 8601 only.
  - date: `YYYY-MM-DD`
  - datetime: `YYYY-MM-DDTHH:MM:SS[.fff][Z|±HH:MM]`
- WebSocket events: exact contracts (see below) with snake_case fields only.

---

### 1) Date/Datetime normalization — BLOCKING

Symptom
- Errors like: `Invalid isoformat string: 'YYYY-MM-DD 00:00:00.000'` when tools or CRUD paths hit non-canonical strings.

Root cause
- Inputs or stored strings use space-separated timestamps; strict parsers reject them.

Strict solution (no fallbacks)
1) Introduce boundary normalizers (single source of truth):
   - File: `nonix_web_db/date_utils.py`
   - `parse_datetime_strict(s: str) -> datetime` (accepts common input variants but always returns a datetime object in canonical form)
   - `parse_date_strict(s: str) -> date` (accepts common input variants, returns `date`)
   - These are used only at boundaries; inside the system all values are proper `date`/`datetime` objects.
2) Apply strictly at:
   - `nonix_web_db/crud/query_processor.py::_coerce_value` to replace `fromisoformat` with strict boundary parsing returning proper types
   - Pydantic schemas with validators for any `date`/`datetime` field (e.g., `nonix_web_music_artist/services/album/album_schemas.py`) to coerce inbound payloads to proper types
3) Serialization: `nonix_web_db/models.py::BaseModel.to_dict` remains `.isoformat()` for real `date`/`datetime` objects; if any value is a string, this is a bug upstream — fix upstream; do not stringify here.

Tests
- Seed data with `release_date` as `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS`, and `YYYY-MM-DDTHH:MM:SS.mmmZ`; all internal values must become proper types and serialize canonically.

---

### 2) Tool message rendering (UI) — HIGH

Symptom
- UI shows “Unknown Tool” and empty parameters while backend content has `tool_name`, `tool_args`.

Strict solution (no fallbacks)
- `vue_libs/nonix-chat/components/message-types/ToolMessage.vue` must read only snake_case keys:
  - `tool_name`, `tool_args`, `execution_status`, `executed_by`, `execution_time`
- Remove CamelCase lookups entirely.
- If historical data exists with CamelCase in DB, perform a one-time migration server-side to write snake_case values; do not branch UI.

---

### 3) Argument propagation (manual, streaming, LangChain) — MEDIUM

Requirement
- All paths must persist and emit identical content shapes.

Contract
- Persisted `tool_call`/`tool_result` content_json must include:
  - `tool_name: string`
  - `tool_args: object`
  - `execution_status: 'success'|'error'|'processing'|'completed'`
  - `executed_by: 'user'|'llm'`
  - `execution_time: ISO-8601 datetime`
  - `execution_path: 'manual'|'streaming'|'langchain'`

Code to verify
- `faster_backend/nonix_web_agentic/services/chat/message_handlers.py`
- `faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py`

---

### 4) WebSocket contracts — MEDIUM

Rooms
- `chat/{session_id}/{history_id}`

Events (must be identical across paths)
- `message_received`:
  - `{ message_id, role, message_type, content, status, timestamp }` (snake_case fields; `content` conforms to contract above for tool messages)
- `tool_status`:
  - `{ tool_name, status, args?, result?, timestamp }` (args/result snake_case; include `args` on started)

UI
- `ChatMessageContainer.vue` handlers consume these shapes and upsert/messages without any key translation.

---

### Next Actions (ordered)
1) Implement strict date utils and integrate into `QueryProcessor` and schema validators.
2) Update `ToolMessage.vue` to snake_case only; remove all CamelCase reads.
3) Re-verify argument propagation and WebSocket event payloads match the contracts everywhere.
4) End-to-end test (manual + LLM paths): dates normalized; UI shows correct tool name/params live without reload.

### References
- `nonix_web_db/crud/query_processor.py` (date coercion)
- `nonix_web_db/models.py` (serialization)
- `nonix_web_music_artist/models/album.py`, `services/album/album_schemas.py` (date fields)
- `vue_libs/nonix-chat/components/message-types/ToolMessage.vue` (UI renderer)


