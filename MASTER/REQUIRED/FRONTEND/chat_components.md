## Chat UI (Personas + Tabs) — Standalone Component (embed many times)

This document explains EXACTLY which files to create, where they live, and how they work to deliver a persona-based chat with multi-tab support as a STANDALONE component. You can drop multiple instances on any page. No router used inside the component. No global stores.

### What you get
- Persona-based chat (pick persona, create sessions per persona)
- Multi-tab chat UI (open many sessions, switch, close, persist tabs)
- Left panel: personas + sessions
- Center: messages + composer
- Right panel: persona tools + MCP server status
- Works without router; deep-linking is handled by the parent page if desired
- All data is live from backend `/api/chat/*` and CRUD endpoints

---

## 1) Backend endpoints this UI uses
- Chat (custom endpoints)
  - POST `/api/chat/sessions` — create session
  - GET `/api/chat/sessions` — list sessions
  - GET `/api/chat/sessions/{id}` — session detail
  - GET `/api/chat/sessions/{id}/messages` — list messages
  - POST `/api/chat/sessions/{id}/send` — send user message
  - POST `/api/chat/sessions/{id}/retry` — retry last user turn
  - GET `/api/chat/personas/{persona_id}/tools` — list persona tools
  - GET `/api/chat/mcp/servers/status` — list MCP servers
- CRUD endpoints (already available)
  - `/api/personas`, `/api/chat-sessions`, `/api/chat-messages`, etc. (used for admin/management screens, not required for basic chat UI)

---

## 2) Files and folders to create (frontend)

Create these under `src/`. Each file is small and focused — no giant “god files”. The main export is a single, embeddable component.

### 2.1 Main standalone component
- `src/components/chat/ChatWidget.vue`
  - The ONE component you embed anywhere
  - Self-contained: no router, no global store, no provide/inject
  - Accepts props for initial persona/session and persistence keys
  - Emits events so the parent can deep-link or track analytics

### 2.2 Services
- `src/services/ChatRuntimeService.js`
  - Thin wrapper around `/api/chat` endpoints for send/retry/tools/mcp
  - Complements existing CRUD services (e.g., `ChatSessionService`) that are used elsewhere for admin

### 2.3 Instance-scoped state (no global store)
- `src/hooks/useChatInstance.js`
  - Factory composable returning reactive state and actions for ONE ChatWidget instance
  - Receives `{ instanceId, persistKey }`
  - State (per instance):
    - `personas`, `sessions`, `openTabs`, `activeTabId`
    - `messagesBySession`, `draftsBySession`
    - `availableToolsByPersona`, `mcpServers`
  - Actions:
    - `loadPersonas`, `loadSessions`, `openSession`, `createSession`, `renameSession`, `closeTab`
    - `loadMessages`, `sendMessage`, `retryLast`, `loadPersonaTools`, `loadMcpStatus`
  - Persists `openTabs`, `activeTabId`, `draftsBySession` to localStorage under `persistKey`

### 2.4 Components (chat)
- `src/components/chat/ChatWorkspace.vue`
  - Used internally by `ChatWidget.vue`
  - Orchestrates header, panels, tabs, center view

- Header (title/actions)
  - `src/components/chat/header/ChatHeader.vue`
    - Shows current session title, persona badge
    - Buttons: new session, rename session, delete session
  - `src/components/chat/persona/PersonaBadge.vue`
    - Small badge with current session’s persona name/icon

- Tabs (sessions)
  - `src/components/chat/tabs/ChatTabs.vue`
    - Tab bar of open sessions (title, active state)
    - New-tab button, close-tab control
  - `src/components/chat/tabs/ChatTab.vue`
    - A single tab item

- Left Panel (navigation)
  - `src/components/chat/panel/LeftPanel.vue`
    - Container layout for left side
  - `src/components/chat/panel/PersonaSelector.vue`
    - List or dropdown of personas (choose persona for new sessions)
  - `src/components/chat/panel/SessionList.vue`
    - Scrollable session list, filter box, click to open
  - `src/components/chat/panel/SessionActions.vue`
    - Buttons: New Session (with selected persona), Clear filters

- Messages (center)
  - `src/components/chat/messages/ChatMessageList.vue`
    - Renders messages for active session (system/user/assistant/tool)
    - Autoscroll-to-bottom except when user scrolls up
  - `src/components/chat/messages/MessageBubble.vue`
    - Displays a single message bubble (user vs assistant vs system)
  - `src/components/chat/messages/ToolCallMessage.vue`
    - Render tool-result style messages (compact JSON view when present)

- Composer (input area)
  - `src/components/chat/composer/ChatComposer.vue`
    - Textarea with send button
    - Shift+Enter for newline, Enter to send
    - Keeps draft per session (syncs with store)
  - `src/components/chat/composer/RetryButton.vue`
    - Retries last assistant turn for active session
  - `src/components/chat/composer/AttachmentButton.vue` (optional stub)
  - `src/components/chat/composer/ToolPicker.vue` (optional stub)

- Right Panel (tools/status)
  - `src/components/chat/panel/RightPanel.vue`
    - Container layout for right side
  - `src/components/chat/panel/ToolList.vue`
    - Shows effective tools for active persona (from `/api/chat/personas/{personaId}/tools`)
    - Simple search/filter
  - `src/components/chat/panel/MCPStatus.vue`
    - Shows MCP servers and status (from `/api/chat/mcp/servers/status`)
    - Refresh button

- Dialogs
  - `src/components/chat/dialogs/NewSessionDialog.vue`
    - Create session: pick persona, title
  - `src/components/chat/dialogs/RenameSessionDialog.vue`
    - Rename current session

- Utilities
  - `src/components/chat/utils/scroll.js`
    - Helpers for autoscroll-to-bottom and freeze-on-scroll-up
  - `src/components/chat/utils/formatting.js`
    - Format message content: plain text, tool outputs

### 2.5 Hooks (composables)
- `src/hooks/useChatApi.js`
  - Wraps `ChatRuntimeService` calls; centralizes error handling
  - API: `createSession`, `listSessions`, `listMessages`, `send`, `retry`, `personaTools`, `mcpStatus`
- `src/hooks/usePersonaTools.js`
  - Derives filtered tool lists per persona; simple client-side search

### 2.6 Router (optional, outside the component)
- The ChatWidget does NOT use the router. If you want deep-linking:
  - Parent page handles the route and passes `initialSessionId` prop
  - Listen to `update:sessionId` to keep URL in sync

### 2.7 Models (JSDoc types for clarity — optional but recommended)
- `src/models/chat.js`
  - `/** @typedef {{ id:number, persona_id:number, title:string, created_by?:string }} ChatSession */`
  - `/** @typedef {{ id:number, session_id:number, role:'system'|'user'|'assistant'|'tool', content_json:any, created_at:string }} ChatMessage */`
  - `/** @typedef {{ id:number, name:string, is_active:boolean, system_prompt?:string }} Persona */`
  - `/** @typedef {{ id:number, name:string, command:string, is_active:boolean }} MCPServer */`

---

## 3) How everything works together (high level data flow)

1) Parent renders `<ChatWidget ... />` (optionally multiple times).
2) `useChatInstance(instanceId, persistKey)` inside the widget loads personas and sessions. If `initialSessionId` provided and not open, it opens that session tab and loads messages.
3) Left panel shows PersonaSelector and SessionList. Selecting a session opens/activates its tab. Creating a new session calls POST `/api/chat/sessions`.
4) Center shows header, tabs, messages, and composer.
   - Sending a message calls POST `/api/chat/sessions/{id}/send`. The store adds the user message optimistically and then appends the assistant response.
   - Retry calls POST `/api/chat/sessions/{id}/retry`.
5) Right panel shows ToolList (`/api/chat/personas/{persona_id}/tools`) and MCPStatus (`/api/chat/mcp/servers/status`).
6) Tabs persist per instance across reloads: `openTabs`, `activeTabId`, and drafts are stored in localStorage under the widget’s `persistKey`. Closing a tab does not delete the session.

---

## 4) UI behavior expectations (simple and predictable)

- Tabs
  - Click tab to activate; middle/close icon to close
  - New tab opens on creating a new session or from SessionList click
  - Persist tabs and drafts in localStorage

- Composer
  - Enter to send, Shift+Enter newline
  - Disabled while sending; draft saved per session

- Message list
  - Autoscroll to bottom on new messages unless user scrolled up
  - Render roles distinctly (user right-aligned, assistant left, system subtle, tool as boxed JSON)

- Panels
  - Left: collapsible on mobile; includes PersonaSelector and Sessions
  - Right: collapsible on mobile; includes Tools list and MCP status

---

## 5) Minimal configuration assumptions

- PrimeVue + PrimeFlex are available (already in project)
- No custom CSS; rely on Prime theme + utilities
- Services are imported directly (no provide/inject). The widget is self-contained.
- Existing CRUD pages handle admin; Chat UI focuses on runtime chat only

---

## 6) Error handling and empty states

- Show inline toasts (PrimeVue ToastService) on API errors
- Empty states for: no sessions, no messages yet, no tools
- Disable buttons while loading/sending

---

## 7) Accessibility and mobile

- Keyboard:
  - Tab navigation across header/tabs/composer
  - Enter to send, Shift+Enter newline
- Mobile:
  - Left/Right panels become off-canvas; accessible via buttons in `ChatHeader`
  - Message list and composer occupy the main view

---

## 8) Quick implementation checklist (in order)

1) Create files/folders exactly as listed in Section 2.
2) (Optional) Parent page sets up deep linking and passes props; ChatWidget itself uses no router.
3) Implement `ChatRuntimeService.js` wrapping `/api/chat` endpoints.
4) Implement `useChatInstance.js` with instance-scoped state, actions, and localStorage persistence.
5) Build `ChatWidget.vue` using `ChatWorkspace.vue`; render header, panels, tabs, messages, composer.
6) Wire LeftPanel → open/create sessions; Center → show messages + send; RightPanel → tools and MCP status.
7) Test: create session, send message, open multiple tabs, close tabs, reload to confirm persistence.

---

## 9) ChatWidget API (props/emits/exposed methods)

- Props
  - `instanceId` (string, required): unique per instance; used for isolation/persistence
  - `initialPersonaId` (number | null)
  - `initialSessionId` (number | null)
  - `persistKey` (string; default: `chat:${instanceId}`)
  - `enableLeftPanel` (boolean; default: true)
  - `enableRightPanel` (boolean; default: true)
  - `maxTabs` (number; default: 8)
  - `readonly` (boolean; default: false)
  - `showMCPStatus` (boolean; default: true)

- Emits
  - `update:sessionId` (number | null)
  - `tab-open` ({ sessionId })
  - `tab-close` ({ sessionId })
  - `message-sent` ({ sessionId, message })
  - `retry` ({ sessionId })
  - `error` ({ source, error })

- Exposed methods (optional via `defineExpose`)
  - `openSession(sessionId)`
  - `createSession({ personaId, title })`
  - `send({ sessionId, content })`
  - `retry({ sessionId })`
  - `renameSession({ sessionId, title })`
  - `closeSessionTab({ sessionId })`

That’s it. Small, focused files; simple responsibilities; zero over-engineering.


