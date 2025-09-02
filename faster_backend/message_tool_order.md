### Message/Tool Ordering: Problem, Cause, and Required Adjustments

#### Problem
- In the database, assistant text messages can appear before the corresponding `tool_call`/`tool_result` entries, giving the appearance of a wrong order when a single assistant turn involves interleaved tool use.
- This is due to streaming persistence/commit timing rather than a logical ordering bug. The system updates and commits assistant text chunks as they arrive; tool messages are created and committed slightly later.

#### What LangChain Streams Guarantee
- `agent.astream_events(...)` yields a strictly ordered event stream within a run.
- Events include parent/child relationships via `run_id` and `parent_ids`. Multiple tools can start/end interleaved with assistant text chunks during one turn.
- There is no guarantee that “assistant message” must be stored strictly after/before tools; interleaving is expected.

#### Root Cause in Our Pipeline
- Assistant text is persisted multiple times during streaming (chunk updates), each with its own commit.
- Tool events (`tool_start` → `tool_call`, `tool_end` → `tool_result`) are created/committed later than some assistant text updates, so their `created_at` follows those earlier commits.
- Relying on `created_at` for rendering therefore misrepresents the logical stream order.

#### Required Adjustments (No fallbacks, one strict structure)
1) Introduce a canonical, monotonic sequence number
- Add a `seq` integer to every persisted streaming item (assistant chunk, tool_call, tool_result, complete, error) within a history/session.
- Increment `seq` for each event as they are consumed from `astream_events` and persisted.
- Use `seq` for ordering in DB queries and UI, not `created_at`.

2) Preserve event topology for threading
- Persist `run_id` (the event id) and `parent_ids` from LangChain for every event we store.
- Define a `turn_id` to group all events belonging to the same assistant turn (top-level chain/agent run or the assistant placeholder message id).
- For tools, persist a `tool_run_id` so `tool_start`/`tool_end` pairs can be matched.

3) Standardize payload fields (snake_case only)
- For WebSocket and DB rows: always include `seq`, `run_id`, `parent_ids`, `turn_id`, `event`, `message_type`, `tool_run_id` (when applicable), `tool_name`, `tool_args`, `result`, `executed_by`, `execution_time`, `execution_path`, `status`, and `timestamp`.
- Frontend strictly reads these top-level fields and never relies on nested fallbacks.

4) UI rendering rules
- Sort by `seq` ascending for deterministic order.
- Group by `turn_id` to display an assistant turn with its interleaved tool events.
- Pair `tool_call` and `tool_result` via `tool_run_id` when presenting tool execution lifecycle.

5) Database querying and history views
- Update history retrieval to order by `seq` instead of `created_at`.
- Ensure pagination uses `seq` for consistent continuation.

6) Validation and invariants
- `seq` must be strictly increasing per history/session.
- All events must carry `turn_id` and `run_id`.
- Tool events must include `tool_run_id` and `tool_name`.
- WebSocket payloads must mirror DB fields exactly (no missing keys, no duplicates).

#### Outcome
- Interleaving remains supported (multiple tools and assistant text in one turn), while order is unambiguous and consistent across DB, WebSocket, and UI.
- No artificial buffering or reordering is needed; we reflect the LangChain event order precisely via `seq`.


### Detailed Implementation Plan

#### Database Model Changes
Add canonical sequencing and threading fields. Prefer minimal, explicit columns and targeted indexes.

1) `chat_messages` (SQLAlchemy model: `faster_backend/nonix_web_agentic/models/chat_message.py`)
- New columns:
  - `seq` INTEGER NOT NULL — strictly increasing per `history_id`
  - `turn_id` VARCHAR(64) NOT NULL — id linking all events in one assistant turn
  - `run_id` VARCHAR(64) NULL — LangChain event/run id for this item
  - `parent_ids` JSON NULL — array of parent run ids from LangChain
  - `tool_run_id` VARCHAR(64) NULL — set for `tool_call` and `tool_result`
- Indexes:
  - `(history_id, seq)` unique index for deterministic ordering and pagination
  - Optional: `(turn_id)` for grouping queries

2) `tool_invocation_logs` (model: `faster_backend/nonix_web_agentic/models/tool_invocation_log.py`)
- New columns:
  - `seq` INTEGER NOT NULL — mirrors the event sequence used when the tool was logged
  - `turn_id` VARCHAR(64) NOT NULL — same turn as its related assistant/message
  - `run_id` VARCHAR(64) NULL — tool run id
  - `parent_ids` JSON NULL — parent run ids
  - `tool_run_id` VARCHAR(64) NOT NULL — required for pairing start/end
- Indexes:
  - `(history_id, seq)`
  - `(history_id, tool_run_id)`

3) New helper table (optional but recommended): `message_sequences`
- Purpose: atomic sequence allocation per `history_id` to avoid race conditions.
- Columns: `history_id` INTEGER PRIMARY KEY, `next_seq` INTEGER NOT NULL
- Model: `faster_backend/nonix_web_agentic/models/message_sequence.py` (new)

4) Migration
- Create Alembic migration adding the new columns/indexes and the `message_sequences` table.
- All new writes must include `seq`.

#### Backend Services/Files To Add or Update

1) New: `SequenceService`
- File: `faster_backend/nonix_web_agentic/services/sequence_service.py`
- API:
  - `async def next_seq(history_id: int) -> int` — allocates and returns the next sequence atomically (using `message_sequences` row with upsert and update in a single transaction).

2) Streaming bridge integration
- File: `faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py`
  - Where handling `ai_start`, `text`, `tool_start`, `tool_end`, `complete`:
    - Allocate `seq = await SequenceService.next_seq(history_id)` per event before persisting.
    - Determine `turn_id` for the current assistant turn (use assistant placeholder message id or a generated UUID stored with the placeholder and reused for all events of the turn).
    - Capture and persist LangChain `run_id` and `parent_ids` from the event metadata if available.
    - For tools: set `tool_run_id` from the LangChain tool run id; ensure both `tool_call` and `tool_result` share it.
  - WebSocket `message_received` payloads must include: `seq`, `turn_id`, `run_id`, `parent_ids`, `tool_run_id` (when applicable).

- File: `faster_backend/nonix_web_agentic/services/chat/streaming_event_manager.py`
  - Ensure all emitted tool/streaming events include `seq`, `turn_id`, `run_id`, `parent_ids`, `tool_run_id` to match DB rows exactly.

- File: `faster_backend/nonix_web_agentic/services/chat/chat_service.py`
  - When normalizing LangChain `LCToolMessage`/events, extract and pass through `run_id`, `parent_ids`, tool run id, and attach them to the event metadata consumed by the mixin.

- File: `faster_backend/nonix_web_agentic/llm/agentic_tool_manager.py`
  - No functional changes required for sequence/threading, but pass through any `run_id`/metadata if surfaced during execution (optional).

3) History retrieval
- File: `faster_backend/nonix_web_agentic/services/chat/message_handlers.py` and any history endpoints
  - Adjust queries to order by `(seq ASC)` instead of `created_at`.
  - Add pagination parameters `since_seq` / `limit` per `history_id`.

#### WebSocket Payload Contract (snake_case, no fallbacks)
Required on every event:
- `message_id`, `history_id`, `role`, `message_type`, `status`, `timestamp`
- `seq`, `turn_id`, `run_id`, `parent_ids` (parent_ids is a list of strings)
- Tool fields when applicable: `tool_run_id`, `tool_name`, `tool_args`, `execution_status`, `result`
- Provenance: `executed_by`, `execution_time`, `execution_path`

Frontend relies solely on these top-level fields.

#### Frontend UI/Component Changes

1) Group by assistant turn
- Data model: store `turn_id` and `seq` for each message/tool event.
- Sorting: by `seq` ascending.
- Pagination: page by turns, not raw messages.

2) New/updated components (under `vue_libs/nonix-chat`)
- New: `components/turns/TurnHeader.vue`
  - Props: `turn`, `toolsUsed`, `status`, `duration`, `firstSeq`, `lastSeq`
  - Shows compact header with assistant summary, tool badges, status indicator; expandable.
- New: `components/turns/TurnTimeline.vue`
  - Renders the interleaved timeline for one turn using `seq` order: assistant chunks, `tool_call`/`tool_result` pairs (paired via `tool_run_id`).
- New: `components/turns/ToolRunBadge.vue`
  - Compact badge with tool name, arg snippet, duration, status.
- Update: `components/message-types/ToolMessage.vue`
  - Read and display `tool_run_id`, `turn_id`, `seq`.
  - No fallbacks to nested/json paths.
- Update: `components/ChatMessageContainer.vue`
  - Maintain a map: `turn_id -> { seqOrderedItems: [...], header: {...} }`.
  - On `message_received` WS, insert by `seq` and group by `turn_id`.
  - Render a list of turns: `TurnHeader` collapsed by default, `TurnTimeline` on expand.

3) Visual indicators
- Live: spinner while a turn has no `complete`/`error` final event.
- Done: checkmark on `complete`, error icon on error; tool badges colored by status.

4) Minimal state logic
- Only trust WS payload fields; do not infer order from timestamps.
- Do not synthesize dummy messages; all items originate from WS with real ids and seq.

#### Testing & Verification
- Unit: sequence allocation atomicity; uniqueness of `(history_id, seq)`.
- Integration: simulate interleaved `on_chat_model_stream`, `on_tool_start`, `on_tool_end`, `complete` and verify DB order by `seq` and UI grouping/rendering.



