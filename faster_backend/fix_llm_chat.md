### LLM chat – precise fix instructions (backend)

— Do not change code here. This file documents exactly what to fix and why —

1) Wrong DB row updated (root cause)
- Problem: Assistant streaming updates the user message row.
- Cause: Argument shifting when scheduling the async task. The task manager consumes the first positional as its own tracking parameter, so worker args are mis-bound.

Evidence (current code):
```441:449:faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py
future = await self.submit_async_task(
    self._process_message_async,
    session_id,  # consumed by task manager as tracking param
    user_msg_id,
    asst_msg_id,
    session_id,  # becomes the worker's 1st positional (WRONG)
    history_id,
    persona_id
)
```
Task manager signature and forwarding:
```58:66:faster_backend/nonix_web_agentic/services/chat/task_manager.py
async def submit_task(self, func: Callable, session_id: int = None, *args, **kwargs)
```
```110:116:faster_backend/nonix_web_agentic/services/chat/task_manager.py
result = await func(*args, **kwargs)
```
Worker expects exactly 5 args, so no TypeError is raised:
```462:469:faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py
async def _process_message_async(self, session_id, user_msg_id, asst_msg_id, history_id, persona_id)
```
Mis-binding that results:
- session_id = user_msg_id
- user_msg_id = asst_msg_id
- asst_msg_id = session_id  ← wrong target id
- history_id = history_id
- persona_id = persona_id

Streaming then writes to the wrong row:
```95:112:faster_backend/nonix_web_agentic/services/chat/streaming_message_handler.py
asst_msg = await db_session.get(ChatMessage, self.assistant_message_id)
asst_msg.content_json = new_content_json
await db_session.commit()
```

Required correction (call site):
- Pass only the worker’s five positionals, in order: (session_id, user_msg_id, asst_msg_id, history_id, persona_id).
- Do not pass a tracking value positionally before them.
- If task tracking is needed, pass the tracking label as a keyword (e.g., session_id=<tracking_id>) to the task manager wrapper so it doesn’t shift the worker args.

2) Meta-type policy (explicit, fixed from frontend)
- Use meta-types as the only stored/routed types; the frontend MUST send them explicitly.
- Allowed meta-types now:
  - user (default for user input)
  - assistant (LLM/AI output)
  - system (system/meta content)
  - tool_call (request to execute a tool)
  - tool_result (result from tool execution)
- Do NOT use "chat" or "text" as stored types.

Inconsistent writer (should be "text"):
```25:33:faster_backend/nonix_web_agentic/services/chat/message_handlers.py
chat_msg = ChatMessage(
    history_id=history_id,
    role='user',
    message_type='chat',  # change to 'text'
    content_json=content,
    status='complete'
)
```

3) Single source of truth for creating user messages
- Ensure only one path creates the user message for the send flow. Avoid duplicate creators that can conflict.

Potential conflict site:
```138:145:faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py
user_msg = ChatMessage(
    history_id=history_id,
    role='user',
    message_type='text',
    content_json=content
)
```

4) Validation checklist (after applying fixes)
- Send a user message:
  - DB: user row has message_type='text' and the exact user text.
  - Assistant placeholder row exists (status='processing').
  - Streaming chunks append to the assistant row only; upon completion, assistant.status='complete' with full text.
- WebSocket events:
  - assistant_message_started → id matches assistant row id.
  - assistant_message_chunk/complete → update the same assistant id.
- No duplicate user messages created by parallel paths.

Notes
- The absence of a Python error is expected: the worker still receives 5 args; they were simply shifted by the wrapper consuming the first positional as a tracking parameter.


2a) Frontend/Backend contract (explicit meta-type)
- Frontend payload MUST include top-level `message_type` ∈ { user | tool_call | system } for sends.
- Payload shape: `{ message_type: 'user', content: { text?: string, attachments?: [...], meta?: {...} } }`.
- Backend `send_message` must read `payload.message_type` (not `payload.content.type`) and route via registry:
  - 'user' → ChatMessageHandler
  - 'tool_call' → ToolCallMessageHandler
  - 'system' → (optional) System handler
- Writers persist meta-types only:
  - user → message_type='user'
  - assistant → message_type='assistant'
  - system → message_type='system'
  - tool_call/tool_result unchanged

Impact scope
- History/streaming logic keys on `role`; changing stored message_type to meta-types does not break it.
- UI renderers should map by meta-type (user/assistant/system/tool_result) and use status for streaming.
- Optional normalization: map old rows (chat/text) to meta-types for consistency.

3a) Streaming normalization (assistant/tool_result)
- Streaming is a state (status), not a type.
- Assistant messages:
  - Create assistant row with `message_type='assistant'`, status='streaming' (or 'processing').
  - Append chunks to that row; on completion, set status='complete'.
  - Never set message_type='streaming'.
- Tool results (if streaming desired): mirror the assistant lifecycle for `message_type='tool_result'` rows: start → chunk → complete.
- WebSocket events drive status transitions; UI selects StreamingMessage by (role/meta-type, status).

Minimal implementation steps (updated)
1. Fix async task call argument order (Section 1 – done).
2. Switch backend routing to top-level `message_type` and register `'user'` (not `'text'`/`'chat'`).
3. Writers: store meta-types (`'user'`, `'assistant'`, `'system'`, `'tool_call'`, `'tool_result'`).
4. Normalize streaming: assistant/tool_result rows stream via status only; no 'streaming' type anywhere.
5. Frontend: send `message_type:'user'`; optimistic `message_type:'user'`; render by meta-type + status (streaming).
6. (Optional) Normalize existing data to meta-types.

Post-fix quick test (meta-types + streaming)
- Send "hi" with `{ message_type:'user', content:{ text:'hi' } }`.
- DB user row: `message_type='user'`, `content_json.text='hi'`.
- Assistant placeholder: `message_type='assistant'`, status='streaming'; chunks arrive; final status='complete'.


2b) Meta-type unification (new demand)
- Goal: Use meta-types as the only stored and routed message types. Default/user input must be `message_type='user'`. Remove 'text' and 'chat' as stored types.
- Meta-types to support now: `user`, `assistant`, `system`, `tool_call`, `tool_result`.
- Attachments and additional data belong in `content` (e.g., `attachments`), not as new `message_type` values.

Backend changes (conceptual; implement where noted):
- API contract for send_message:
  - Require top-level `message_type: 'user'|'tool_call'|'system'`.
  - Keep `content` for the payload (e.g., `{ text?: string, attachments?: [...] }`).
  - Stop reading `payload.content.type`.
- Handler registry (ChatMessageMixin.__init__):
  - Register `'user'` → ChatMessageHandler, `'tool_call'` → ToolCallMessageHandler. Add `'system'` if needed.
- Writers:
  - User writer: store `message_type='user'`.
  - Assistant writer/placeholder: store `message_type='assistant'`.
  - System writer: store `message_type='system'` when used.
  - Tool-flow unchanged: `'tool_call'` and `'tool_result'`.
- Helpers:
  - `_get_last_user_message_content` default type should be `'user'`.
- WebSocket events:
  - Prefer including `message_type` alongside `role`, `content`, `timestamp` so UI doesn’t infer.

Frontend changes (conceptual; implement where noted):
- Sending:
  - Send `{ message_type: 'user', content: { text: '...' } }` for user messages.
- Optimistic:
  - Use `message_type: 'user'` for new local entries.
- Rendering:
  - Map meta-types to components: `'user'` → TextMessage, `'assistant'` → TextMessage (or a distinct assistant view if desired), `'system'` → SystemMessage, `'tool'/'tool_result'` as today.
  - Remove reliance on `'text'`/`'chat'` in UI mappings.
- Upsert:
  - Prefer backend-provided `message_type`; otherwise derive from `role` (`user`/`assistant`/`system`).

Normalization plan (data, optional):
- Existing rows:
  - role='user' & message_type in {'text','chat'} → 'user'
  - role='assistant' & message_type='text' → 'assistant'
  - role='system' & message_type='text' → 'system'
  - Tool rows unchanged

Minimal implementation steps (updated)
1. Fix async task call argument order (Section 1 – done).
2. Switch backend routing to top-level `message_type` and register `'user'` (not `'text'`/`'chat'`).
3. Writers: store meta-types (`'user'`, `'assistant'`, `'system'`, `'tool_call'`, `'tool_result'`).
4. Frontend: send `message_type:'user'`; optimistic `message_type:'user'`; adjust renderer mappings to meta-types.
5. (Optional) Normalize existing data to meta-types.

Post-fix quick test (meta-type)
- Send "hi" with `{ message_type:'user', content:{ text:'hi' } }`.
- DB user row: `message_type='user'`, `content_json.text='hi'`.
- Assistant placeholder: `message_type='assistant'`; streaming updates that row only; final assistant row has full text.


