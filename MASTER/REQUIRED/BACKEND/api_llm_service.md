## Backend LLM/Chat Service – Architecture, Data Model, and API

This document specifies the LLM/Chat backend service so all chat behavior, personas, tool access, and MCP configuration are runtime-changeable and persisted in the database. It aligns with BIG-PICTURE: tool-first chat, persona-configured access, hybrid internal tools + MCP, persistent history, simple permissions via tool lists.

### Current codebase status (verified)
- APIRouter exists and auto-registers services via `@expose` methods.
- Generic `CrudService` exists and drives REST endpoints via config.
- Models in place: `AIProvider`, `AIModelMapping`, `AIAnalysisResult`.
- Chat-specific models/services do NOT exist yet (personas, tools, MCP, sessions, messages, invocation logs).

### Goals
- Everything is runtime-changeable: all chat/LLM configs and state stored in DB.
- Chat is tool-first; the LLM may call tools within persona-scoped permissions.
- Hybrid tool access: internal tools (built-in) + external MCP tools.
- Persistent chat history with sessions/messages; auditable tool invocation logs.

---

## Data Model (to add)

All tables are SQLite-friendly and portable to Postgres/MySQL.

### 0) Providers and Model Mappings (updated)
- AIProvider
  - id (PK)
  - name (string, unique)
  - provider_type (string) – e.g., `openai`, `anthropic`, `google`
  - module (string) – Python module to import, e.g., `langchain_openai`
  - class (string) – class to instantiate, e.g., `ChatOpenAI`
  - method (string, default `invoke`) – instance method to call
  - config_json (JSON) – connection/credential props only (e.g., `api_key`, `base_url`, timeouts)
  - is_active (bool)
  - created_at, updated_at

- AIModelMapping
  - id (PK)
  - provider_id (FK AIProvider)
  - model_name (string) – provider model identifier (e.g., `gpt-4o-mini`, `claude-3-haiku-20240307`)
  - parameters_json (JSON, nullable) – run-time params (e.g., `temperature`, `max_tokens`)
  - is_active (bool)
  - created_at, updated_at

### 1) Personas and Access
- Persona
  - id (PK)
  - name (string, unique)
  - is_active (bool, default true)
  - system_prompt (text, nullable) – persona instructions for the LLM
  - metadata_json (JSON, nullable) – arbitrary persona data
  - created_at, updated_at (timestamps)

- InternalTool
  - id (PK)
  - namespace (string) – e.g., "artist", "file", "admin"
  - name (string) – e.g., "list_albums", "read_lyrics"
  - qualified_name (string, unique) – "namespace:name" for lookup
  - description (text)
  - config_json (JSON, nullable) – tool-specific config
  - is_active (bool)
  - created_at, updated_at

- PersonaToolAccess (many-to-many with wildcards)
  - id (PK)
  - persona_id (FK Persona)
  - pattern (string) – supports exact `namespace:name` or wildcard `namespace:*`
  - allow (bool, default true)
  - created_at

### 2) External MCP Servers
- MCPServer
  - id (PK)
  - name (string, unique)
  - command (string) – e.g., `npx -y @modelcontextprotocol/server-filesystem`
  - args_json (JSON) – array of CLI args
  - env_json (JSON, nullable) – env vars for the process
  - is_active (bool)
  - created_at, updated_at

- PersonaMCPServer (many-to-many)
  - id (PK)
  - persona_id (FK Persona)
  - mcp_server_id (FK MCPServer)
  - override_args_json (JSON, nullable)
  - override_env_json (JSON, nullable)
  - is_active (bool)
  - created_at

### 3) Sessions, Messages, Tool Logs
- ChatSession
  - id (PK)
  - persona_id (FK Persona)
  - title (string)
  - created_by (string, nullable) – user identifier
  - metadata_json (JSON, nullable)
  - created_at, updated_at

- ChatMessage
  - id (PK)
  - session_id (FK ChatSession)
  - role (enum/string): system | user | assistant | tool
  - content_json (JSON) – structured content; for tool role, includes tool name + output
  - created_at

- ToolInvocationLog
  - id (PK)
  - session_id (FK ChatSession)
  - message_id (FK ChatMessage, nullable) – the triggering message
  - tool_name (string) – `namespace:name` or `mcp_server:tool`
  - input_json (JSON)
  - output_json (JSON, nullable)
  - status (string): success | error
  - started_at, completed_at, duration_ms

### 4) Chat Model Selection
- Each persona MUST reference its model via `ai_model_mapping_id`.
- Persona must have an active model mapping; otherwise chat returns an error and does not proceed.

---

## Services and Endpoints

All CRUD-style services follow the existing `CrudService` pattern and are auto-registered via `APIRouter`.

### CRUD Services (standard endpoints)
For each service below, the router will expose:
- POST `/api/{service}/` – create
- GET `/api/{service}/` – list (with filters, pagination, sorting)
- GET `/api/{service}/{id}` – read
- PUT `/api/{service}/{id}` – update
- DELETE `/api/{service}/{id}` – delete
- GET `/api/{service}/search` – search
- POST `/api/{service}/bulk` – bulk ops
- GET `/api/{service}/selector` – selector

Implement the following services by extending `CrudService` with model + config:
- `Personas` → PersonaService
- `internal-tools` → InternalToolService
- `persona-tool-access` → PersonaToolAccessService
- `mcp-servers` → MCPServerService
- `persona-mcp-servers` → PersonaMCPServerService
- `chat-sessions` → ChatSessionService
- `chat-messages` → ChatMessageService
- `tool-invocation-logs` → ToolInvocationLogService

### Chat Service (custom endpoints)
`ChatService` handles the chat loop and tool calls. Endpoints:
- POST `/api/chat/sessions` – create a new session
  - body: `{ persona_id, title?, created_by?, system_prompt_override?, metadata? }`
  - returns: session object and initial system message created if applicable

- GET `/api/chat/sessions` – list sessions (filters: `persona_id`, `created_by`)

- GET `/api/chat/sessions/{id}` – session detail

- GET `/api/chat/sessions/{id}/messages` – list messages (paginated)

- POST `/api/chat/sessions/{id}/send` – send a user message and get assistant response
  - body: `{ content, attachments?, metadata? }`
  - behavior:
    1) persist user message
    2) resolve persona, system prompt, and chat model (from persona.ai_model_mapping_id)
    3) compile available tools = internal allowed by `PersonaToolAccess` + MCP tools from attached servers
    4) call LLM via provider-defined module/class/method with merged props; future: execute tool calls within allowlist; log each call in `ToolInvocationLog`
    5) persist assistant final message
    6) return assistant final message

- POST `/api/chat/sessions/{id}/retry` – retry the last assistant turn (re-run with same context)

- GET `/api/chat/personas/{persona_id}/tools` – resolve effective tool allowlist for a persona (expanded from patterns)

- GET `/api/chat/mcp/servers/status` – list MCP servers and indicate active/usable state

---

## Chat Flow Details

### Tool Resolution
- Internal tools: stored in `InternalTool` table. At runtime, each `qualified_name` maps to a registered Python function. A small registry maps `qualified_name` → callable.
- Persona allowlist: union of explicit tools and wildcard patterns applied to active internal tool set.
- MCP tools: for each active `PersonaMCPServer`, start/connect to the server (or reuse a managed connection) and list exposed tools; include them in the runtime tool map under `serverName:toolName`. (Execution PENDING)

### Message/Content JSON Shapes
- user/assistant message `content_json` example:
  ```json
  { "type": "text", "text": "Show me albums by TRC" }
  ```
- tool message `content_json` example:
  ```json
  { "type": "tool_result", "tool": "artist:list_albums", "input": {"artist_id": 1}, "output": {"albums": [ ... ]} }
  ```

### Safety & Permissions
- Before executing a tool, check persona allowlist. If not permitted, return an LLM-visible error message; do not execute.
- For MCP, only connect to servers assigned to the persona and marked `is_active`.

### Tool Invocation API
- Internal tools: provider may return a tool call `{ "type": "tool_call", "tool": "namespace:name", "args": { ... } }`.
- ChatService will:
  - Check allowlist; execute via in-process registry; log to `tool_invocation_logs`; append a `tool` message; optionally follow with assistant acknowledgment.
- Endpoint: `POST /api/chat/personas/{persona_id}/tools/execute` for on-demand execution with body `{ tool, args, session_id?, message_id? }` (allowlist enforced).

### Model Selection & Provider Execution
- Provider construction is DB-driven from `AIProvider` fields:
  - Import `module`, get `class`, instantiate with kwargs built by merging:
    - Provider `config_json` (connection and credentials only, e.g., `api_key`, `base_url`)
    - `model` = `AIModelMapping.model_name`
    - Overrides from `AIModelMapping.parameters_json` (e.g., `temperature`, `max_tokens`)
  - Call the instance `method` (default `invoke`) with LangChain-formatted messages.
- Returns assistant text; on errors, returns a readable message and does not crash.
- If the persona has no active mapping/provider, the service returns a clear error; no fallback behavior.

---

## Implementation Plan (backend)

1) Add models (SQLAlchemy): Persona, InternalTool, PersonaToolAccess, MCPServer, PersonaMCPServer, ChatSession, ChatMessage, ToolInvocationLog. Optionally extend `AIModelMapping` with `persona_id`.
2) Create services extending `CrudService` for each model with appropriate configs (filters, sorting, validation, selector fields).
3) Implement `ChatService` with the custom endpoints above using `@expose`. (DONE)
4) Internal tool registry: a Python module that registers callables keyed by `qualified_name` from DB; examples: `artist:list_albums`, `artist:create_album`, `file:read_lyrics`, `admin:system_info`.
5) MCP client manager: a lightweight manager to spawn/connect to configured MCP servers on demand and list/execute tools for requests. (PENDING UI integration; DB models ready)
6) Register new services in `backend/app/__init__.py` with `api_router.register_service(...)`.

Notes:
- Current project relies on `db.create_all()`; adding these models and re-running init will create the tables. Consider Alembic later for migrations.

---

## Frontend Interfaces (high level)
- Management screens driven by generic CRUD for Personas, Tools, MCP Servers, Access rules.
- Chat UI consuming chat endpoints:
  - session list/create
  - message thread view (stream/poll), send message, retry
  - persona switcher and available tools panel

---

## Alignment with BIG-PICTURE
- Tool-first chat with hybrid internal + MCP tools
- Persona-based access via simple config stored in DB
- Persistent chat history and logs in DB
- Model mappings reused via `AIModelMapping` referenced directly by persona
- Minimal, extensible architecture using existing APIRouter + CrudService patterns

---

## Provider and Mapping JSON Examples

### OpenAI (standard)
```json
{
  "name": "openai-main",
  "provider_type": "openai",
  "module": "langchain_openai",
  "class": "ChatOpenAI",
  "method": "invoke",
  "config_json": {
    "api_key": "sk-REPLACE_ME",
    "base_url": "https://api.openai.com/v1"
  },
  "is_active": true
}
```

### Anthropic
```json
{
  "name": "anthropic-main",
  "provider_type": "anthropic",
  "module": "langchain_anthropic",
  "class": "ChatAnthropic",
  "method": "invoke",
  "config_json": {
    "api_key": "sk-ant-REPLACE_ME"
  },
  "is_active": true
}
```

### Google (Gemini)
```json
{
  "name": "google-genai",
  "provider_type": "google",
  "module": "langchain_google_genai",
  "class": "ChatGoogleGenerativeAI",
  "method": "invoke",
  "config_json": {
    "api_key": "AIza-REPLACE_ME"
  },
  "is_active": true
}
```

### OpenAI-compatible Proxy
```json
{
  "name": "openai-proxy",
  "provider_type": "openai",
  "module": "langchain_openai",
  "class": "ChatOpenAI",
  "method": "invoke",
  "config_json": {
    "api_key": "sk-proxy-REPLACE_ME",
    "base_url": "https://your-proxy.example.com/v1"
  },
  "is_active": true
}
```

### Mapping (shared shape)
```json
{
  "provider_id": 1,
  "model_name": "gpt-4o-mini",
  "parameters_json": { "temperature": 0.2, "max_tokens": 512 },
  "is_active": true
}
```

### Merge/Precedence Rules
- Instantiate provider class with kwargs merged in this order:
  - Provider `config_json`
  - `model` = `model_name` from mapping
  - Overrides from `parameters_json`
- Call `method` (default `invoke`) with LangChain-formatted messages.

### Persona Requirements (strict)
- `ai_model_mapping_id` on `Persona` is required. No persona or missing mapping → no chat.
- Optional `artist_id` on `Persona` allows scoping tools/data to that artist.


