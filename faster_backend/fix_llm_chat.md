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

Example writer (target meta-type):
```25:33:faster_backend/nonix_web_agentic/services/chat/message_handlers.py
chat_msg = ChatMessage(
    history_id=history_id,
    role='user',
    message_type='user',
    content_json=content,
    status='complete'
)
```

3) Single source of truth for creating user messages
- Ensure only one path creates the user message for the send flow. Remove/avoid duplicate creators that can conflict.

- 4) Validation checklist (after applying fixes)
- Send a user message:
  - DB: user row has message_type='user' and the exact user text.
  - Assistant placeholder row exists (status='streaming' or 'processing').
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

4) Frontend architecture (containers + base message)
- OutgoingMessageContainer (send)
  - Purpose: wraps user-sent messages
  - State: sending (optimistic), processing, failed, complete
  - Actions: delete, copy, retry, cancel (while sending)
  - Child layout: UserMessage (non-streaming)
- IncomingMessageContainer (receive)
  - Purpose: wraps backend-originated messages (assistant, tool_result, system)
  - State: streaming, processing, complete, error
  - Actions: delete, copy, stop (while streaming)
  - Child layouts: AssistantMessage / ToolMessage / SystemMessage
- Base component: BackendMessage (shared features)
  - Props: id, message_type, role, status, content_json, created_at
  - Behavior: show streaming state while status ∈ {processing, streaming}; append chunks; switch to final view on complete; show errors; common actions
  - All backend messages are streamable by default; can be disabled via flag when needed

5) Mapping (meta-type → container + layout)
- message_type='user' → OutgoingMessageContainer(UserMessage)
- message_type='assistant' → IncomingMessageContainer(AssistantMessage)
- message_type='tool_result' → IncomingMessageContainer(ToolMessage)
- message_type='system' → IncomingMessageContainer(SystemMessage)
- No 'streaming' type; wrappers switch views by status only

6) Standardized props/events (UI contract)
- Common props (both containers): id, message_type, role, status, content_json, created_at, canDelete, canCopy, isStreamable
- Emits (both): delete(id), copy(id), error(id, details)
- Outgoing extras: retry(id), cancel(id)
- Incoming extras: stop(id), appendChunk(id, chunk), complete(id, finalContent)

7) Event payload contract (runtime)
- Always include: message_id, message_type, role, status, content (chunk/final), timestamp
- Event sequence (incoming): started → chunk* → complete | error
- UI upserts by message_id; no full list reload after send

8) Frontend legacy removals
- Do not register or use 'chat' or 'streaming' as message types
- Map strictly by meta-types; use status to decide streaming vs final view

Minimal implementation steps (updated)
1. Fix async task call argument order (Section 1 – done).
2. Switch backend routing to top-level `message_type` and register `'user'` (not `'text'`/`'chat'`).
3. Writers: store meta-types (`'user'`, `'assistant'`, `'system'`, `'tool_call'`, `'tool_result'`).
4. Normalize streaming: assistant/tool_result rows stream via status only; no 'streaming' type anywhere.
5. Frontend: send `message_type:'user'`; optimistic `message_type:'user'`; render by meta-type + status (streaming).
6. Frontend: introduce OutgoingMessageContainer (user) and IncomingMessageContainer (assistant/tool_result/system) with BackendMessage base features.
7. Frontend: remove legacy 'chat'/'streaming' registrations; map strictly by meta-type.
8. (Optional) Normalize existing data to meta-types.

Post-fix quick test (meta-types + streaming)
- Send "hi" with `{ message_type:'user', content:{ text:'hi' } }`.
- DB user row: `message_type='user'`, `content_json.text='hi'`.
- Assistant placeholder: `message_type='assistant'`, status='streaming'; chunks arrive; final status='complete'.
 - UI: shows OutgoingMessageContainer for the user row; IncomingMessageContainer for the assistant row; stop button visible while streaming; no duplicate rows; no full reload.


<!-- Duplicate older section removed to keep a single, authoritative meta-type policy above. -->


