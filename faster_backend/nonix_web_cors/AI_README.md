# AI_README: Nonix CORS Plugin API

## Requirements
- Python 3.8+
- fastapi
- nonix_web
- nonix_plugin
- nonix_di

## Core Classes & Interfaces

### CORS Plugin
```python
class NxWebCORSPlugin(BasePlugin):
    """CORS middleware plugin for FastAPI"""
    def __init__(self, config: Dict[str, Any]) -> None
    def _configure(self, config: Dict[str, Any]) -> None: """Configure CORS middleware"""
    # Public attributes
    web_server: NxWebServer
```

## Integration Points
```python
# Enable CORS plugin
settings.PLUGINS = [
    {"name": "web"},
    {
        "name": "cors",
        "config": {
            "allow_origins": ["http://localhost:3000", "https://myapp.com"],
            "allow_credentials": true,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"]
        }
    }
]

# Automatic CORS headers added to all responses
# No manual integration needed - works automatically
```

## Configuration Schema
```json
{
  "name": "cors",
  "version": "1.0.0",
  "class": "NxWebCORSPlugin",
  "dependencies": ["web"],
  "config": {
    "allow_origins": ["*"],
    "allow_credentials": true,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"]
  }
}
```
