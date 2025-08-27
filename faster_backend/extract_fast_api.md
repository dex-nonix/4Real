# Refactoring NxWebServer to encapsulate FastAPI

## Goal
Switch `NxWebServer` from inheriting `FastAPI` to encapsulating a `FastAPI` instance in `self.app`. Plugins and services will interact with `server.app` for FastAPI APIs, while keeping the rest of the server and plugin system intact for later adjustments.

## Impacted files and concrete changes (based on current code)

### faster_backend/nonix_web/server.py
- **Class**: Change `class NxWebServer(FastAPI):` to `class NxWebServer:` and add `self.app = FastAPI(...)` in `__init__` with the same args now passed to `super().__init__` (title, debug, lifespan, docs_url, redoc_url, openapi_url).
- **PluginManager wiring**: Keep `PluginManager(self, ...)` unchanged. Plugins will switch to `server.app` internally, so the manager should continue passing the `NxWebServer` instance.
- **Exception handler**: Change `@self.exception_handler(Exception)` to `@self.app.exception_handler(Exception)`.
- **WebSocket enablement hook**: Keep `self.sio` attribute ownership on `NxWebServer`. Mounting the `socketio.ASGIApp` should happen via plugins to `server.app` (see websocket plugin). No WSGI middleware is needed; mount the ASGI app directly.
- **Gunicorn/uvicorn entry**: Update `run_gunicorn` to expose the FastAPI app object:
  - Use `uvicorn.run(lambda: cls(settings).app, ..., factory=True)` or add a `gunicorn_app` property returning `self.app` and use `lambda: cls(settings).gunicorn_app`.

### faster_backend/nonix_web/plugin/base_plugin.py
- **Router registration**: Change `server.include_router(routed_service.to_router(server), prefix="/api")` to `server.app.include_router(routed_service.to_router(server), prefix="/api")`.
- Type hints remain `server: "NxWebServer"` for `configure/startup/shutdown`.

### faster_backend/nonix_web/plugin/plugin_manager.py
- No change. It should continue to pass the `NxWebServer` instance (`self.server`) to plugins for access to both `server.app` and `server.sio`.

### faster_backend/nonix_web/services/base_service.py
- Keep `to_router(cls, app, ...)` receiving the `NxWebServer` instance (unchanged call sites). Inside services, `self.app` will be an `NxWebServer`, so `await self.app.sio.emit(...)` remains valid when websocket is enabled by the plugin. No refactor required here.

### Plugins (file-by-file)
- faster_backend/nonix_web_cors/plugin.py
  - Change `server.add_middleware(...)` to `server.app.add_middleware(...)`.

- faster_backend/nonix_web_websocket/plugin.py
  - Keep creating `sio = socketio.AsyncServer(...)` and `sio_app = socketio.ASGIApp(sio)`.
  - Change `server.mount(config["path"], sio_app)` to `server.app.mount(config["path"], sio_app)`.
  - Assign `server.sio = sio` so services that call `self.app.sio.emit(...)` work.

- faster_backend/nonix_web_open_api/plugin.py
  - Route decorators: change `@server.get(...)` to `@server.app.get(...)` (for both OpenAPI JSON and docs endpoints).
  - When building OpenAPI: replace `server.title/version/openapi_version/description/routes/openapi_tags/servers` with `server.app.title/.../server.app.routes/...`.
  - Optionally pass `server.app` into `custom_openapi(app, tags=...)` to keep that function operating on a FastAPI instance.

- faster_backend/nonix_web_static_files/plugin.py
  - Change `server.mount(...)` to `server.app.mount(...)`.

- faster_backend/nonix_web_db/plugin.py
  - No changes needed (does not call FastAPI APIs).

- faster_backend/nonix_web_music_artist/plugin.py, faster_backend/nonix_web_file_manager/plugin.py, faster_backend/nonix_web_agentic/plugin.py
  - No direct FastAPI calls; they just declare `api_services`. No change required beyond BasePlugin handling.

### faster_backend/main.py
- Keep `NxWebServer.run_gunicorn(settings)` invocation. Implementation inside `server.py` will be updated to serve `NxWebServer(...).app`.

## API usage mapping for refactor
- `server.include_router(...)` → `server.app.include_router(...)` (BasePlugin)
- `server.add_middleware(...)` → `server.app.add_middleware(...)` (CORS)
- `server.mount(path, app)` → `server.app.mount(path, app)` (Websocket, Static files)
- `@server.get(...)` → `@server.app.get(...)` (OpenAPI plugin)
- `server.title/version/.../routes/...` → `server.app.title/version/.../routes/...` (OpenAPI plugin)
- Ensure websocket plugin sets `server.sio` after creating the `AsyncServer`.

## Notes
- Do not switch to `WSGIMiddleware`. Socket.IO `ASGIApp` mounts directly on the FastAPI app via `app.mount(...)`.
- Keeping `PluginManager` passing the `NxWebServer` instance preserves access to both `server.app` and `server.sio` for plugins and services.
