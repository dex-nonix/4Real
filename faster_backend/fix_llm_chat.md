# LLM Chat Streaming Fixes (post-refactor)

## Goal
Restore streaming chat by standardizing on `StreamingChunk` (no dicts), fixing AI model mapping retrieval, and aligning conversation history with LangChain expectations. Also ensure no duplicate user messages are sent and validate tool and websocket integration.

## Required changes (actionable checklist)

### 1) Consume only StreamingChunk in async processor
- File: `faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py`
- Method: `_process_message_async`
- Issue: The loop treats streamed items like dicts (`message_dict.get(...)`). However, `run_chat_streaming(...)` yields `StreamingChunk` objects.
- Action:
  - Replace the local conversion block that builds a `StreamingChunk` from a dict with direct usage of the yielded item.
  - Expected handling shape inside the loop:
    - Use `message.content`, `message.chunk_type`, `message.metadata`, `message.is_final` directly.
    - Keep downstream calls intact (`update_content_safely`, `emit_chunk_event`, `emit_tool_event`, `finalize_assistant_message`).

### 2) Fix AI model mapping lookup
- File: `faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py`
- Method: `_resolve_ai_model`
- Issue: Queries `AIModelMapping` with `id == persona_id` instead of the persona's mapping id.
- Action:
  - Fetch `AIModelMapping` by `persona.ai_model_mapping_id`.
  - Alternatively, pass forward the mapping object identified in `_select_chat_model` to avoid re-query drift.

### 3) Align conversation_history with LangChain expectations
- File: `faster_backend/nonix_web_agentic/services/chat/chat_service.py`
- Method: `run_chat_streaming`
- Issue: Builds `conversation_history` as prefixed strings ("Human: ...", "Assistant: ..."), while `ChatPromptTemplate` with `MessagesPlaceholder("chat_history")` expects message tuples or BaseMessage instances.
- Action:
  - Build `chat_history` as a list compatible with the prompt/runnable, e.g. tuples like `("system", text)`, `("human", text)`, `("ai", text)`.
  - Do not add an extra raw user message if the prompt already includes `{input}`; keep a single source of truth.

### 4) Avoid duplicate user messages sent to the model
- File: `faster_backend/nonix_web_agentic/services/chat/chat_service.py`
- Method: `run_chat_streaming`
- Issue: The model receives both a prefixed "Human: ..." and a separate `input` user message.
- Action:
  - Ensure only one user input flows into the chain: either feed all via `chat_history` or only via the `{input}` variable, but not both.

### 5) Tools availability (if tools are expected) 
- Files:
  - `faster_backend/nonix_web_agentic/plugin.py`
  - Tool registration site(s) for `AgenticToolManager`
- Issue: `AgenticToolManager` is instantiated but no actual tool callables are registered; persona allowlist thus yields 0 tools.
- Action:
  - Register tool functions into `AgenticToolManager` during plugin configuration or a dedicated init step.
  - Ensure `PersonaToolAccess.pattern` entries match the registered `qualified_name` values so `list_persona_tools` and `create_langchain_tools` expose them.

### 6) Websocket service injection in frontend
- Files (consumer-side check):
  - `vue_libs/nonix-chat/components/*.vue`
  - App-level DI where `chat-service` is provided
- Issue: Components call `onWebSocketEvent/joinRoom/leaveRoom` on the injected `chat-service`, but the provided `vue_libs/nonix-chat/services/ChatService.js` is REST-only.
- Action:
  - Confirm the application injects a websocket-enabled service instance under the `chat-service` key (wrapping both REST and websocket). If not, provide the correct instance to match component expectations.

## Validation steps
1) Send a chat message; confirm no exception about `'StreamingChunk' object has no attribute 'get'`.
2) Observe WS events:
   - `assistant_message_started` → placeholder appears/typing indicator.
   - `assistant_message_chunk` → content grows incrementally.
   - `assistant_message_complete` → status switches to complete; no error banner.
3) Verify OpenAI/LangChain payloads do not contain duplicated user entries.
4) If tools are configured, confirm `🔧 Created N LangChain tools` with N > 0 and tool events are emitted.

## Pseudocode references (do not apply directly; for clarity only)

- Streaming consumer (shape inside `_process_message_async` loop):
  - When receiving `message: StreamingChunk`:
    - text → `message.chunk_type == "text"` then append `message.content`
    - start → `ai_start`/`tool_start` emit events
    - end → `tool_end`/`complete` finalize and emit

- Conversation history formation for LangChain:
  - Replace prefixed strings with tuples matching the prompt/runnable format, and avoid duplicating the user content between `chat_history` and `input`.
