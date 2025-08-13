## Chat UI Phases — Step-by-step plan (dummy-proof)

Simple, linear checklist to build the persona-based, multi-tab ChatWidget as a standalone component (no router inside; can be embedded multiple times). Each phase has: goal, tasks, acceptance, and quick test steps.

Prerequisites (one-time)
- Backend running with ChatService and CRUD endpoints
- Frontend runs (PrimeVue/PrimeFlex ready)
- Read `MASTER/REQUIRED/FRONTEND/chat_components.md` for the full file structure

---

Phase 0 — Widget Placeholder (no router)
- Goal: Render a placeholder ChatWidget anywhere
- Tasks
  - Create `src/components/chat/ChatWidget.vue` with a simple placeholder
  - Add it to any view (e.g., `Home.vue`): `<ChatWidget instance-id="main" />`
- Acceptance
  - The placeholder renders; no errors
- Test
  - Drop two instances with different `instance-id`; both render independently

Phase 1 — Chat Runtime Service
- Goal: Single service for `/api/chat` endpoints
- Tasks
  - Create `src/services/ChatRuntimeService.js`
  - Implement: `createSession`, `listSessions`, `getSession`, `listMessages`, `send`, `retry`, `personaTools`, `mcpStatus`
- Acceptance
  - Each method returns a Promise and handles errors consistently
- Test
  - Temporarily call methods from `ChatWidget` on mount (console.log results)

Phase 2 — Instance State Skeleton (no global store)
- Goal: Per-instance state (personas, sessions, tabs, messages)
- Tasks
  - Create `src/hooks/useChatInstance.js`
  - State: `personas`, `sessions`, `openTabs`, `activeTabId`, `messagesBySession`, `draftsBySession`, `availableToolsByPersona`, `mcpServers`
  - Actions: `loadPersonas`, `loadSessions`, `openSession`, `createSession`, `closeTab`, `loadMessages`
  - Persist `openTabs`, `activeTabId`, `draftsBySession` to localStorage under `persistKey`
- Acceptance
  - Factory returns isolated state per `instanceId`; persistence works
- Test
  - Open/close tabs in two widgets; states do not interfere

Phase 3 — Workspace Shell
- Goal: 3-zone layout (left panel, center, right panel)
- Tasks
  - Create `ChatWorkspace.vue`, `LeftPanel.vue`, `RightPanel.vue`, `ChatHeader.vue`
  - Render the shell inside `ChatWidget.vue`
- Acceptance
  - Shell renders with visible header and empty panels
- Test
  - Confirm layout inside any page, multiple instances ok

Phase 4 — Personas & Sessions (Left Panel)
- Goal: List personas and sessions; open a session
- Tasks
  - Components: `PersonaSelector.vue`, `SessionList.vue`, `SessionActions.vue`
  - Wire actions: `loadPersonas`, `loadSessions`, `openSession`
  - Clicking a session opens a tab (or activates existing)
- Acceptance
  - Personas visible; sessions listed; clicking a session opens a tab
- Test
  - Click multiple sessions; tabs appear

Phase 5 — Tabs Bar
- Goal: Manage tabs (open/activate/close)
- Tasks
  - Components: `ChatTabs.vue`, `ChatTab.vue`
  - Keep `openTabs` and `activeTabId` per instance/localStorage
  - Closing tab does NOT delete the session
- Acceptance
  - Multiple tabs show; switching works; closing leaves others intact
- Test
  - Open 2–3 sessions; close one; reload; tabs persist per instance

Phase 6 — Messages List
- Goal: Load and display messages for active session
- Tasks
  - Components: `ChatMessageList.vue`, `MessageBubble.vue`, `ToolCallMessage.vue`
  - Action: `loadMessages(sessionId)` caches under `messagesBySession`
  - Roles: `system`, `user`, `assistant`, `tool`
- Acceptance
  - Opening a tab loads messages; roles render distinctly
- Test
  - Verify system/user/assistant/tool styles

Phase 7 — Composer (Send & Retry)
- Goal: Send message; retry last turn
- Tasks
  - Components: `ChatComposer.vue`, `RetryButton.vue`
  - Actions: `sendMessage(sessionId, content)`, `retryLast(sessionId)`
  - Draft persistence per session via `draftsBySession`
- Acceptance
  - Enter to send; Shift+Enter newline; retry works
- Test
  - Send/Retry and verify updates

Phase 8 — Right Panel (Tools & MCP)
- Goal: Show persona tools and MCP server status
- Tasks
  - Components: `ToolList.vue`, `MCPStatus.vue`
  - Fetch tools `/api/chat/personas/{persona_id}/tools`
  - Fetch MCP `/api/chat/mcp/servers/status`
- Acceptance
  - Tool list and MCP status render and refresh
- Test
  - Switch personas; tool list updates; MCP list loads

Phase 9 — Autoscroll & Mobile
- Goal: Smooth autoscroll and mobile panels
- Tasks
  - Utils: `scroll.js` for autoscroll-to-bottom, freeze on scroll up
  - Responsive: Collapse left/right panels on small screens; toggle via header
- Acceptance
  - New messages auto-scroll unless user scrolled up; panels toggle on mobile
- Test
  - Send while scrolled up; verify behavior

Phase 10 — Errors & Empty States
- Goal: Friendly UX when data missing/errors occur
- Tasks
  - Use PrimeVue Toasts in hooks error paths
  - Empty prompts: “No sessions”, “No messages yet”, “No tools available”
- Acceptance
  - Errors surface as toasts; empty states clear
- Test
  - Simulate network error; verify toasts

Phase 11 — Parent Deep Links & Reload (Optional)
- Goal: Parent page controls deep links; widget stays router-free
- Tasks
  - Parent passes `initialSessionId` prop from route
  - Parent listens to `update:sessionId` to sync URL
  - Tabs/drafts already persist per instance via localStorage
- Acceptance
  - Visiting route opens session via props; reload restores tabs per instance
- Test
  - Change route param; widget updates active tab

Phase 12 — Admin Links (Optional)
- Goal: Link to CRUD pages for Personas, Tools, etc.
- Tasks
  - Parent page renders nav links to `/personas`, `/internal-tools`, `/persona-tool-access`, `/mcp-servers`
- Acceptance
  - Links navigate to existing CRUD pages
- Test
  - Navigate successfully

Phase 13 — Real LLM Hookup (Optional)
- Goal: Replace placeholder assistant reply with real LLM call
- Tasks
  - Configure `AIModelMapping` (`purpose='chat'`)
  - Update backend ChatService to call provider (keep tool allowlist checks)
- Acceptance
  - Assistant responses come from real provider
- Test
  - Responses change when switching model mapping

---

Deliverables per phase
- Files created/updated (as per tasks)
- Basic manual test performed (as per test steps)
- Phase accepted when acceptance criteria are met

Time-saving tips
- Build UI with minimal styling (PrimeVue + PrimeFlex)
- Keep components small and focused; avoid “god files”
- No router or global store inside the widget; parent owns deep linking

Reference
- See `MASTER/REQUIRED/FRONTEND/chat_components.md` for exact file/folder list and responsibilities


