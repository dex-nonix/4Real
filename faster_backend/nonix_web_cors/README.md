# Nonix CORS Plugin - Usage Guide

## Overview

The Nonix CORS Plugin provides Cross-Origin Resource Sharing (CORS) support for the Nonix Web Server. It integrates FastAPI's CORSMiddleware to handle cross-origin requests, allowing web applications from different domains to access your API.

**⚠️ Important Philosophy**: This plugin enables secure cross-origin communication. Configure origins carefully for production security.

## Dependencies

### Required Systems
- Nonix Web Server (`nonix_web`)
- FastAPI CORSMiddleware
- Plugin system for integration

### Optional Features
- Custom origin validation
- Credential support
- Method-specific permissions

## Quick Start

### 1. Basic Setup
```python
from nonix_web.config import Settings
from nonix_web.server import NxWebServer

settings = Settings()
settings.PLUGINS = [
    {"name": "cors"}
]

NxWebServer.run_gunicorn(settings)
```

### 2. Configure Origins
```python
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["http://localhost:3000", "https://myapp.com"]
        }
    }
]
```

### 3. Basic Usage
```python
# CORS headers automatically added to all responses
# Frontend can now make cross-origin requests
```

## Using the CORS Plugin

### Basic Configuration
```python
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["https://frontend.example.com"],
            "allow_credentials": true,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"]
        }
    }
]
```

### Development Configuration
```python
# Allow all origins for development
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["*"],
            "allow_credentials": false,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }
    }
]
```

### Production Configuration
```python
# Restrict origins for security
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": [
                "https://myapp.com",
                "https://admin.myapp.com"
            ],
            "allow_credentials": true,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Authorization", "Content-Type"]
        }
    }
]
```

## Architecture

### Core Components
- **NxWebCORSPlugin**: Main plugin class
- **CORSMiddleware**: FastAPI CORS middleware integration
- **Configuration**: Origin and permission settings

### Data Flow
1. **Plugin Load**: CORS plugin initializes
2. **Middleware Registration**: CORSMiddleware added to FastAPI app
3. **Request Processing**: CORS headers added to responses
4. **Origin Validation**: Requests validated against allowed origins

### Plugin Integration
The plugin integrates with the web server through:
- Automatic middleware registration
- Configuration-driven setup
- Request/response header management

## Advanced Usage Patterns

### Multiple Origins
```python
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": [
                "https://app.example.com",
                "https://staging.example.com",
                "https://admin.example.com"
            ]
        }
    }
]
```

### Credential Support
```python
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["https://trusted-app.com"],
            "allow_credentials": true,  # Allows cookies/auth headers
            "allow_headers": ["Authorization", "Content-Type"]
        }
    }
]
```

### Method Restrictions
```python
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["https://myapp.com"],
            "allow_methods": ["GET", "POST"],  # Only allow specific methods
            "allow_headers": ["Content-Type"]
        }
    }
]
```

## Integration Examples

### SPA Integration
```python
# Frontend hosted separately from API
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["http://localhost:3000"],  # React dev server
            "allow_credentials": true,
            "allow_headers": ["Authorization", "Content-Type"]
        }
    }
]
```

### Mobile App Integration
```python
# Mobile apps need CORS for API access
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["capacitor://localhost"],  # Capacitor apps
            "allow_credentials": true
        }
    }
]
```

### Multi-Domain Setup
```python
# Multiple frontend applications
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": [
                "https://web.myapp.com",
                "https://mobile.myapp.com",
                "https://admin.myapp.com"
            ],
            "allow_credentials": true
        }
    }
]
```

## Best Practices

### Security Configuration
```python
# Production: Restrict origins
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["https://trusted-domain.com"],
            "allow_credentials": true,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Authorization", "Content-Type"]
        }
    }
]
```

### Development Configuration
```python
# Development: More permissive
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["http://localhost:3000", "http://localhost:8080"],
            "allow_credentials": false,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }
    }
]
```

### Header Management
```python
# Specify exact headers needed
settings.PLUGINS = [
    {
        "name": "cors",
        "config": {
            "allow_origins": ["https://myapp.com"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With"
            ]
        }
    }
]
```

## Troubleshooting

### Common Issues

**CORS errors in browser**
```javascript
// Browser console shows CORS error
Access to XMLHttpRequest at 'https://api.example.com' 
from origin 'https://frontend.example.com' has been blocked by CORS policy
```

**Solutions:**
- Check `allow_origins` includes your frontend domain
- Verify `allow_credentials` is set correctly
- Ensure required headers are in `allow_headers`

**Preflight request failures**
```javascript
// OPTIONS request blocked
// Solution: Add required headers to allow_headers
```

**Cookie/auth header issues**
```javascript
// Auth headers blocked
// Solution: Set allow_credentials: true
```

### Debug Information
```python
# Enable detailed CORS logging
settings.LOG_LEVEL = "debug"

# Check middleware registration
# Verify configuration values
```

### Support Resources
- FastAPI CORS documentation
- MDN CORS reference
- Browser developer tools network tab
