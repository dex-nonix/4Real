# Nonix Web Server - Usage Guide

## Overview

The Nonix Web Server provides HTTP REST API and WebSocket server functionality. It integrates FastAPI for REST endpoints and Socket.IO for real-time communication, with built-in plugin system support.

**⚠️ Important Philosophy**: This package provides the core web server infrastructure. Use plugins to extend functionality rather than modifying the server directly.

## Dependencies

### Required Systems
- Python 3.8+
- FastAPI for REST API functionality
- Socket.IO for WebSocket support
- Plugin system for extensibility

### Optional Features
- Database integration (via plugins)
- Authentication (via plugins)
- File handling (via plugins)

## Quick Start

### 1. Basic Setup
```python
from nonix_web.config import Settings
from nonix_web.server import NxWebServer

settings = Settings()
settings.APP_NAME = "MyWebApp"
settings.DEBUG = True

NxWebServer.run_gunicorn(settings)
```

### 2. Enable Plugins
```python
settings.PLUGINS = [
    {"name": "cors"},
    {"name": "auth"},
    {"name": "database"}
]
```

### 3. Basic Usage
```python
# Server starts with plugin functionality
# Access at http://localhost:5000
```

## Using the Web Server

### Basic Operations
```python
from nonix_web.config import Settings
from nonix_web.server import NxWebServer

# Configure server
settings = Settings()
settings.HOST = "0.0.0.0"
settings.PORT = 8000
settings.WS_ENABLED = True

# Start server
server = NxWebServer(settings)
```

### Plugin Integration
```python
# Plugins extend server functionality
settings.PLUGINS = [
    {"name": "api-plugin", "config": {"prefix": "/api"}},
    {"name": "websocket-plugin"}
]
```

### Router Creation
```python
from nonix_web.router.decorators import router, route
from nonix_web.router.web_server_router import NxWebServerRouter

@router("/api/users", tags=["Users"])
class UserRouter(NxWebServerRouter):

    @route("", methods=["GET"])
    async def get_users(self):
        # Plugin-provided service
        return await self.service_call_and_respond(
            user_service.get_all_users
        )
```

## Architecture

### Core Components
- **NxWebServer**: Main server orchestrator
- **NxWebServerRouter**: Base class for API routes
- **NxWebServerWebSocketService**: WebSocket communication
- **Settings**: Configuration management

### Data Flow
1. **Configuration**: Settings define server behavior
2. **Plugin Loading**: Plugins extend server capabilities
3. **Router Registration**: API routes are registered
4. **Server Start**: FastAPI/Socket.IO servers start

### Plugin Integration
The server integrates with plugins through:
- Automatic plugin discovery
- Service registration
- Router registration
- Configuration override

## Advanced Usage Patterns

### Custom Configuration
```python
settings = Settings()
settings.LOG_LEVEL = "debug"
settings.PLUGIN_SEARCH_PATH = ["./plugins", "/opt/plugins"]
settings.WS_ALLOWED_ORIGINS = ["https://myapp.com"]
```

### WebSocket Integration
```python
# WebSocket enabled automatically
settings.WS_ENABLED = True

# Send messages from routes
await self.ws_service.send_ws_message(
    room="notifications",
    message={"event": "update", "data": payload}
)
```

### Plugin Development
```python
from nonix_web.decorator import web_routers

@web_routers([MyRouter], prefix="/api/v1")
class MyPlugin(BasePlugin):
    def _configure(self, config):
        # Plugin configures server
        pass
```

## Integration Examples

### Framework Integration
```python
# Integrate with FastAPI ecosystem
from fastapi.middleware.cors import CORSMiddleware

# Add middleware via plugins
settings.PLUGINS = [{"name": "cors-plugin"}]
```

### Plugin-Based Architecture
```python
# Server as plugin host
settings.PLUGINS = [
    {"name": "auth-plugin"},
    {"name": "api-plugin"},
    {"name": "websocket-plugin"}
]

# Plugins provide functionality
# Server provides the foundation
```

### Production Deployment
```python
# Production configuration
settings.DEBUG = False
settings.HOST = "0.0.0.0"
settings.PORT = 80

NxWebServer.run_gunicorn(settings)
```

## Best Practices

### Configuration
```python
# Use environment variables
import os
settings.HOST = os.getenv("HOST", "localhost")
settings.PORT = int(os.getenv("PORT", "5000"))
```

### Plugin Organization
```python
# Group related functionality
settings.PLUGINS = [
    # Core functionality
    {"name": "auth"},
    {"name": "database"},

    # API endpoints
    {"name": "user-api"},
    {"name": "product-api"},

    # Real-time features
    {"name": "notifications"}
]
```

### Error Handling
```python
# Use service_call_and_respond for consistent errors
return await self.service_call_and_respond(
    my_service.do_work,
    service_args=(param,),
    response_converter=lambda r: {"result": r}
)
```

## Troubleshooting

### Common Issues

**Server won't start**
```bash
# Check plugin dependencies
# Verify configuration
# Check port availability
```

**WebSocket connections fail**
```python
# Verify WS_ENABLED = True
# Check WS_ALLOWED_ORIGINS
# Confirm Socket.IO client configuration
```

**Plugin loading errors**
```python
# Check plugin directory exists
# Verify plugin.json is valid
# Confirm plugin class inherits BasePlugin
```

### Debug Information
```python
# Enable debug logging
settings.LOG_LEVEL = "debug"
settings.LOG_OUTPUT = ["console"]
```

### Support Resources
- Check plugin documentation
- Review server logs
- Verify configuration syntax