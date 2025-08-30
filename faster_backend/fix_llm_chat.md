### LLM chat – end-to-end fixes and final architecture (frontend + backend)

— Reference record of what changed, why, and how it behaves now —

1) Core policies (authoritative)
- message_type (meta-types only): user | assistant | system | tool_call | tool_result
- Streaming is a status, not a type: streaming | processing | complete | error
- Frontend must send top-level message_type; backend routes by it; no legacy 'chat' or 'text' storage
- All backend-originated messages stream by default, except system messages (non-streaming by default, streamable by flag)

2) Backend fixes and endpoints
- Argument mis-binding fixed (prevents assistant chunks writing into user rows)
  - In ChatMessageMixin.submit_message_for_async_processing → submit task with correct worker args order: (user_msg_id, asst_msg_id, history_id, persona_id, session_id)
  - Worker signature: _process_message_async(self, user_msg_id, asst_msg_id, history_id, persona_id, session_id)
  - StreamingMessageHandler.assistant_message_id is set to asst_msg_id and all DB writes target that row only

- Meta-type routing and writers
  - ChatMessageMixin.__init__: message_type_registry.register('user', ChatMessageHandler())
  - ChatMessageMixin.send_message: reads payload.message_type (top-level), not content.type
  - ChatMessageHandler: writes user rows with message_type='user', status='complete'
  - Assistant placeholder: message_type='assistant', status='processing'
  - Tool result: message_type='tool_result'

- Streaming events (WebSocket)
  - assistant_message_started → { message_id, status:'streaming' }
  - assistant_message_chunk → { message_id, chunk }
  - assistant_message_complete → { message_id, status:'complete' }
  - streaming_error → { message_id, error_message }
  - All emitted to room chat/{session_id}/{history_id}

- Per-request (per-assistant message) cancel
  - New endpoint: POST /chat/sessions/{session_id}/histories/{history_id}/messages/{assistant_message_id}/cancel
  - Implementation: tags the asyncio Task with _assistant_message_id at submission; cancel endpoint finds and cancels exactly that task; no session-level cancel remains

3) Frontend behavior and components
- Optimistic UI for user messages
  - On send: push a temporary user row with id 'temp-<ts>' and status='sending'
  - On message_received (role user): replace the most recent optimistic 'sending' user entry with the backend row, not pushing a duplicate

- Assistant streaming lifecycle (status-driven)
  - On assistant_message_started: ensure/create assistant row with status='streaming'
  - On assistant_message_chunk: append to the assistant row by message_id; if start was missed, create the row on first chunk
  - On assistant_message_complete: set status='complete'; if all previous events were missed, create the row with accumulated content and status='complete'

- Stop button → per-message cancel
  - Finds the current assistant row with status='streaming' and calls ChatService.cancelMessage(sessionId, historyId, assistantMessageId)

- Renderer, mapping, and status logic
  - Container renders per message_type with status control:
    - user → UserMessage (non-streaming)
    - assistant → StreamingMessage (status-driven: while streaming shows typing; on complete shows final)
    - tool_result → ToolMessage (should include the same streaming feature set; separate design)
    - system → SystemMessage (non-streaming by default; streamable by flag)
  - getMessageComponent: for assistant rows in status='streaming' shows the live typing; complete/error shows final content

4) Files touched (key excerpts)
- faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py
  - Fixed task submission args; added per-message cancel endpoint; assistant placeholder writes meta-type and status; user writer uses message_type='user'
- faster_backend/nonix_web_agentic/services/chat/streaming_event_manager.py
  - Emits started/chunk/complete/error with assistant message_id
- faster_backend/nonix_web_agentic/services/chat/message_handlers.py
  - User writer uses message_type='user'; tool result uses message_type='tool_result'; events include message_type and status
- vue_libs/nonix-chat/components/ChatMessageContainer.vue
  - User optimistic status='sending' and replace on message_received
  - Assistant start/chunk/complete handlers: create/append/finalize with fallbacks if earlier events missed
  - Stop button calls cancelMessage(sessionId, historyId, assistantMessageId)
  - getMessageComponent uses live view for assistant while status='streaming'
- vue_libs/nonix-chat/services/ChatService.js
  - Added cancelMessage(sessionId, historyId, assistantMessageId)
- vue_libs/nonix-chat/components/message-types/StreamingMessage.vue
  - Live typing UI; subscribes to chunk/complete/error by message_id; maintains local streaming content and typing animation

5) Final contracts (what to send/receive)
- Frontend send payload
  - { message_type:'user' | 'tool_call' | 'system', content:{ text?: string, ... } }
- Backend stores meta-types only; status drives streaming; no 'streaming' as type
- WebSocket assistant events always include the assistant message_id and never the user id

6) Defaults for streaming
- AssistantMessage: streaming by default
- ToolMessage: streaming by default (tool layout; same features)
- SystemMessage: not streaming by default (enable streaming via flag when needed)

7) Known good flow (quick checklist)
- Send "hi"
  - UI: shows one user row (status='sending'), then replaced by backend row (status='complete'); not duplicated
  - Backend: creates assistant placeholder (status='processing'), emits started (UI shows typing), emits chunks (UI appends), emits complete (UI marks complete)
  - Cancel: while streaming, Stop cancels only that assistant message task
  - Reload: assistant rows with status='complete' render final text; no "typing" shown

8) Shared streaming logic
- Extract shared streaming logic into a composable (useStreamingMessage) and use it in AssistantMessage/ToolMessage. SystemMessage uses the same API but is configured non-streaming by default.


