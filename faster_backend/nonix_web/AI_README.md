# AI_README: Nonix Web Server API

## Requirements
- Python 3.8+
- fastapi
- socketio
- uvicorn
- nonix_plugin
- nonix_di

## Core Classes & Interfaces

### Web Server
```python
class NxWebServer:
    """Main FastAPI web server with Socket.IO support"""
    def __init__(self, settings: Settings) -> None
    def run_gunicorn(self, settings: Settings) -> None: """Run with Gunicorn WSGI server"""
    async def _lifespan(self, app: FastAPI) -> AsyncGenerator: """ASGI lifespan handler"""
    async def _setup_server(self) -> None: """Initialize server resources"""
    async def _teardown_server(self) -> None: """Cleanup server resources"""
    def _setup_logging(self) -> None: """Configure logging system"""
    def _enable_websocket(self) -> None: """Enable Socket.IO WebSocket support"""
    def __init__server(self) -> None: """Initialize server components"""
    # Public attributes
    sio: AsyncServer
    plugin_manager: NxPluginManager
    app: FastAPI
    settings: Settings
```

### WebSocket Service
```python
class NxWebServerWebSocketService:
    """WebSocket messaging service"""
    def __init__(self) -> None
    async def send_ws_message(self, room: str, message: dict) -> None: """Send WebSocket message to room"""
    # Public attributes
    sio: AsyncServer
```

### Settings Configuration
```python
class Settings:
    """Web server configuration settings"""
    # Public attributes
    APP_NAME: str
    DEBUG: bool
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_DATE_FORMAT: str
    LOG_OUTPUT: list
    LOG_FILE_PATH: str
    LOG_MAX_SIZE: int
    LOG_BACKUP_COUNT: int
    WS_ENABLED: bool
    WS_ALLOWED_ORIGINS: str
    HOST: str
    PORT: int
    PLUGIN_SEARCH_PATH: list
    PLUGINS: list
```

## Decorators
```python
def router(prefix: str = None, tags: list = None, **kwargs) -> Callable:
    """Decorator to register FastAPI router classes"""

def route(path: str, methods: list = None, **kwargs) -> Callable:
    """Decorator to register individual route methods"""
```

## Integration Points
```python
# Create and configure server
from nonix_web.config import Settings
from nonix_web.server import NxWebServer

settings = Settings()
settings.APP_NAME = "MyApp"
settings.DEBUG = True
settings.PLUGINS = [
    {"name": "cors"},
    {"name": "database"}
]

server = NxWebServer(settings)
server.run_gunicorn(settings)

# Inject web server in plugins
from nonix_di import NxInject

class MyPlugin(BasePlugin):
    web_server: NxWebServer = NxInject(NxWebServer)
    fastapi_app: FastAPI = NxInject(FastAPI)

# WebSocket messaging
from nonix_di import NxInject

class MyService:
    ws_service: NxWebServerWebSocketService = NxInject(NxWebServerWebSocketService)

    async def send_notification(self, user_id: str, message: dict):
        await self.ws_service.send_ws_message(f"user_{user_id}", message)

# Router registration (in plugins)
@router("/api/users", tags=["Users"])
class UserRouter:
    def get_users(self):
        return {"users": []}

# Route registration (in router classes)
class ApiRouter:
    @route("/health", methods=["GET"])
    def health_check(self):
        return {"status": "healthy"}
```

## Configuration Schema
```json
{
  "name": "web",
  "version": "1.0.0",
  "class": "NxWebServer",
  "config": {
    "app_name": "MyWebApp",
    "debug": false,
    "host": "0.0.0.0",
    "port": 5000,
    "ws_enabled": true,
    "plugin_search_path": ["./plugins"],
    "plugins": [
      {"name": "cors"},
      {"name": "database"}
    ]
  }
}
```
