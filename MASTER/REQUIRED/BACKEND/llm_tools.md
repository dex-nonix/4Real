## LLM Tools – Internal, MCP, and Persona-Scoped Partials

This document defines how tools are modeled, resolved, and executed at runtime. The design is persona-first, partials-based, and requires no argument injection.

### Goals
- Persona controls which tools are available and how they behave.
- Artist personas get tools pre-bound to their `artist_id` via partials.
- Non-artist personas use the same tools without pre-binding; they must pass required arguments explicitly.
- Internal tools (in-process callables) and MCP tools (external servers) are both supported.
- Optional use of `backend/libs/nonix_llm` to define tools with metadata, hidden props, and runtime partials.

---

## Data Model (already in codebase)

- InternalTool
  - Global catalog of internal tools with `qualified_name` and `config_json`.

- PersonaToolAccess
  - Per-persona allowlist via patterns (e.g., `artist:*`, `file:read_lyrics`).

- MCPServer
  - Catalog of external MCP servers with `command`, `args_json`, `env_json`.

- PersonaMCPServer
  - Per-persona assignment of MCP servers with overrides and `is_active`.

No schema changes needed for partials; composition happens at runtime.

---

## Internal Tools – Registry and Partials

- Global registry maps `qualified_name` → callable.
- Persona tool resolution builds a persona-scoped tool map:
  - If `persona.artist_id` is set:
    - For tools whose first parameter is `artist_id`, expose `functools.partial(func, artist_id=persona.artist_id)` under the same `qualified_name`.
    - Other tools remain unwrapped.
  - If no `artist_id`, expose original functions (caller must pass `artist_id` when needed).
- Execution: look up the persona-scoped callable and call with provided args. No argument injection or mutation.

Notes:
- Keep the global registry immutable; build a per-request/per-persona tool map.
- Signature detection: `inspect.signature(func)` to check the first parameter name if needed.
- You can also pre-bind additional kwargs (e.g., `locale`, `page_size`) using partials.

---

## MCP Tools – Adapters

- MCP tools are accessed via configured servers (`MCPServer` + `PersonaMCPServer`).
- Expose thin adapter functions that call MCP endpoints.
- Pre-bind server name, auth, or sandbox root via adapter defaults (kwargs) so LLM sees minimal, safe parameters.
- Adapters can be defined with `nonix_llm` (see below) to hide sensitive properties.

---

## Optional: nonix_llm Library Integration

`backend/libs/nonix_llm` provides:
- `@llm_tool` decorator to define tools with:
  - `description`, `param_descriptions`
  - `props` (default kwargs)
  - `hidden_props` (not exposed to LLM)
  - `partial=[...]` (bind runtime objects/kwargs)
- `NxLLMToolsManager` to load tools from:
  - Config dicts/files/directories
  - Modules, class instances, standalone functions

How to combine:
- At persona tool resolution, compute a prebind dict (e.g., `{ artist_id, root_path, bind_root, locale }`).
- Produce partials by passing these as `props`/`partial` into `@llm_tool` or when loading via manager.
- Expose only remaining parameters to the LLM; hidden props stay unavailable to the model.

Benefits:
- Stable, minimal tool signatures per persona.
- Built-in path safety (`resolve_safe_path`) for file operations.
- Config-driven tool bundles without code changes.

---

## Runtime Flow (Chat)

1) Resolve persona for the session.
2) Build allowlist from `PersonaToolAccess` over active `InternalTool`s; include MCP adapters for assigned servers.
3) Persona-scoped composition:
   - Internal: wrap allowed functions in partials if `persona.artist_id` is set and the first param is `artist_id`.
   - MCP: wrap adapters with pre-bound defaults (e.g., server, root path) as needed.
4) Expose the persona-scoped tool map to the LLM.
5) When LLM calls a tool, execute the callable with provided args. No injection.
6) Log invocations in `tool_invocation_logs`. Append tool results to chat.

---

## Examples

### Internal tool: album_list

```python
def album_list(artist_id: int, page: int = 1, page_size: int = 20) -> dict:
    # Returns albums for the artist
    ...
```

- Artist persona (artist_id=7): expose `partial(album_list, artist_id=7)` → LLM calls `album_list(page=1)`.
- General persona: expose `album_list` as-is → LLM must call `album_list(artist_id=7, page=1)`.

### MCP adapter

```python
def fs_read(path: str, *, server: str, root_path: str, bind_root: bool = True) -> str:
    # Calls MCP filesystem tool on `server`, enforcing sandbox under root_path
    ...
```

- Persona prebinds: `{ server: 'files', root_path: '/artists/7', bind_root: True }` → LLM calls `fs_read(path='lyrics.txt')`.

---

## Error Handling
- If a required parameter is not pre-bound and not provided, the function error is returned as a readable message.
- Unauthorized tools (not in allowlist) return an explicit “not allowed” error.

---

## Summary
- Persona-scoped partials provide context-aware simplicity without hidden magic.
- Internal and MCP tools are unified under a simple callable interface.
- Optional `nonix_llm` adds metadata, hidden props, and config-driven loading to improve safety and UX.

