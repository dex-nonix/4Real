### Message/Tool Ordering — Phased Integration Plan (DB → Backend → UI)

This plan is grounded in the current codebase. It implements canonical `seq` ordering and tooling topology across database, backend logic, and UI.

### Phase 1 — Database Migration and Models

Goal: Add canonical sequencing and topology fields; provide atomic sequence allocation; prepare indexes.

- Files to update (exist):
  - `faster_backend/nonix_web_agentic/models/chat_message.py`
    - Add columns: `seq` (INTEGER, NOT NULL), `turn_id` (VARCHAR(64), NOT NULL), `run_id` (VARCHAR(64), NULL), `parent_ids` (JSON, NULL), `tool_run_id` (VARCHAR(64), NULL).
    - Indexes: `(history_id, seq)` unique; optional `(turn_id)`.
  - `faster_backend/nonix_web_agentic/models/tool_invocation_log.py`
    - Add columns: `seq` (INTEGER, NOT NULL), `turn_id` (VARCHAR(64), NOT NULL), `run_id` (VARCHAR(64), NULL), `parent_ids` (JSON, NULL), `tool_run_id` (VARCHAR(64), NOT NULL).
    - Indexes: `(history_id, seq)`, `(history_id, tool_run_id)`.

- Files to add (new):
  - `faster_backend/nonix_web_agentic/models/message_sequence.py`
    - Table `message_sequences(history_id PK, next_seq INTEGER NOT NULL)` for atomic allocation per history.

- Pydantic schemas to update (exist):
  - `faster_backend/nonix_web_agentic/services/chat_message/chat_message_schemas.py`
    - Include fields: `seq`, `turn_id`, `run_id`, `parent_ids`, `tool_run_id` in relevant models (Base/Create/Update/Response).
  - `faster_backend/nonix_web_agentic/services/tool_invocation_log/tool_invocation_log_schemas.py`
    - Include: `seq`, `turn_id`, `run_id`, `parent_ids`, `tool_run_id`.

- Alembic migration (framework present via `requirements.txt`; repo has no migrations dir yet):
  - If not initialized, initialize Alembic for `nonix_web_db` metadata.
  - Create migration to add new columns and indexes; create `message_sequences`.

Exit criteria:
- New columns and indexes present; constraints enforce monotonic `(history_id, seq)`.


### Phase 2 — Backend Sequencing and Persistence

Goal: Ensure every persisted streaming item and tool lifecycle event carries `seq`/`turn_id`/`run_id`/`parent_ids`/`tool_run_id`. Use `seq` for history ordering.

- Files to add (new):
  - `faster_backend/nonix_web_agentic/services/sequence_service.py`
    - `async def next_seq(history_id: int) -> int` — atomically increments `message_sequences.next_seq` in a single transaction and returns the allocated `seq`.

- Files to update (exist):
  - `faster_backend/nonix_web_agentic/services/chat/chat_service.py`
    - `emit_chat_event(...)`, `emit_tool_event(...)`: ensure downstream payloads will include new top-level fields provided by mixins/managers.
    - `run_chat_streaming` uses `iter_messages(...)` (see `llm/llm_message_utils.py`) and creates `StreamingChunk`s; metadata must propagate to event manager.
  - `faster_backend/nonix_web_agentic/services/chat/streaming_event_manager.py`
    - In `emit_chunk_event(...)`: include `seq`, `turn_id`, `run_id`, `parent_ids`, and `tool_run_id` on all emitted WS payloads based on chunk metadata.
  - `faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py`
    - `create_assistant_placeholder(...)`: assign a `turn_id` that will be reused for the turn; persist placeholder with `seq`.
    - `_process_message_async(...)`: before persisting or emitting for each event (`ai_start`, `text`, `complete`, `error`, `tool_start`, `tool_end`), allocate `seq = await SequenceService.next_seq(history_id)` and persist to `ChatMessage`/`ToolInvocationLog`.
    - `_build_chat_history(...)`: change ordering to `seq` ascending instead of `created_at` (currently orders by `created_at`).
    - `_execute_tool_call(...)`: ensure both `tool_call` and `tool_result` messages share a `tool_run_id`; allocate and persist `seq` for each; include `turn_id`/`run_id`/`parent_ids`.
  - `faster_backend/nonix_web_agentic/services/chat/mixins/chat_history_mixin.py`
    - For any history + messages retrieval endpoints, order messages by `seq ASC`; add pagination using `since_seq` and `limit`.
  - `faster_backend/nonix_web_agentic/services/chat_message/chat_message_service.py`
    - Update CRUD `sorting` to allow and default to `seq` for list endpoints.

Exit criteria:
- Every persisted event carries `seq`; WS payloads contain the required top-level fields; history queries order by `seq`.


### Phase 3 — WebSocket Payload Contract and Tool Pairing

Goal: Standardize WS event payloads and ensure tool start/end are paired via `tool_run_id`.

- Files to update (exist):
  - `faster_backend/nonix_web_agentic/services/chat/streaming_event_manager.py`
    - For `tool_start`/`tool_end`, propagate `tool_run_id`, `tool_name`, `args`, and `result` in top-level fields.
  - `faster_backend/nonix_web_agentic/services/chat/message_handlers.py`
    - `message_received` payloads for user/tool calls: include `seq`, `turn_id`, `run_id`, `parent_ids`, `tool_run_id` when applicable.
  - `faster_backend/nonix_web_agentic/llm/llm_message_utils.py`
    - Ensure `iter_messages(...)` surfaces `run_id` and any parent topology so downstream can persist `run_id`/`parent_ids`.

Exit criteria:
- All WS events have consistent top-level fields; tools paired by `tool_run_id`.


### Phase 4 — Frontend UI: Turn Grouping and Interleaved Timeline

Goal: Render messages ordered by `seq`, grouped by `turn_id`, and show tool lifecycle alongside assistant text.

- Files to add (new):
  - `vue_libs/nonix-chat/components/turns/TurnHeader.vue`
  - `vue_libs/nonix-chat/components/turns/TurnTimeline.vue`
  - `vue_libs/nonix-chat/components/turns/ToolRunBadge.vue`

- Files to update (exist):
  - `vue_libs/nonix-chat/components/ChatMessageContainer.vue`
    - On WS `message_received` and streaming events, upsert into a `turns` map keyed by `turn_id` and ordered by `seq`.
    - Render a list of turns: `TurnHeader` (summary) and expandable `TurnTimeline` (interleaved assistant chunks, tool calls/results).
    - Stop relying on timestamps for ordering.
  - `vue_libs/nonix-chat/components/message-types/ToolMessage.vue`
    - Read top-level `tool_name`, `tool_args`, `execution_status`, `result`, `executed_by`, `execution_time`; display condensed badge or timeline entry.

- Optional admin screens (exist):
  - `src/services/ChatMessageService.js` and `src/services/ToolInvocationLogService.js` can add `seq` sorting for grids.

Exit criteria:
- UI displays assistant turns with deterministic `seq` order and paired tool runs.


### Phase 5 — Validation and Rollout

Goal: Verify correctness and stability across layers.

- Tests and checks:
  - Streaming run: Confirm that interleaved tool events and assistant chunks arrive and render in `seq` order.
  - Pagination: Server returns correct pages using `since_seq + limit`; client appends without reordering.
  - Tool pairing: UI shows `tool_call` and `tool_result` matched by `tool_run_id` within a turn.

Exit criteria:
- Stable operation with no ordering regressions; UIs reflect precise event order.


