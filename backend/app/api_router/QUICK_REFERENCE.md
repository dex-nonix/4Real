# API Router Quick Reference

## Quick Start

```python
from app.api_router import APIRouter

# Create router
router = APIRouter()

# Register service
router.register_service('my-service', MyService)

# Get Flask blueprint
app.register_blueprint(router.blueprint, url_prefix='/api')
```

## Service Architecture

### **BaseApiService** (NEW!)

All services now extend `BaseApiService` which provides automatic Swagger generation:

```python
from app.services.base_api_service import BaseApiService

class MyService(BaseApiService):
    # Automatically gets to_swagger() method
    # Automatically gets method_to_swagger() method
    pass
```

### **CrudService** (Enhanced!)

CRUD services automatically generate schemas from models and configs:

```python
from app.services.crud_service import CrudService

class ArtistService(CrudService):
    model = Artist  # Automatically generates schemas
    config = {
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name']
        }
    }
    # Gets automatic Create/Update/Response schemas!
```

### **Custom Services** (Simple!)

Custom services use `@expose` decorator for schemas:

```python
class ChatService(BaseApiService):
    @expose(
        '/sessions',
        methods=['POST'],
        tags=["Chat"],
        request_schema={"type": "object", "properties": {...}},
        response_schema={"type": "object", "properties": {...}}
    )
    def create_session(self, req):
        pass
```

## Service Filtering (New Feature!)

### **Backend Filtering (Query Parameters)**

Filter OpenAPI documentation to focus on specific services:

```
# All services
GET /api/openapi.json

# Single service
GET /api/openapi.json?services=chat

# Multiple services
GET /api/openapi.json?services=chat,artists,albums

# Services with spaces (auto-trimmed)
GET /api/openapi.json?services=chat, artists , albums
```

### **Frontend Filtering (Swagger UI)**

The Swagger UI now has a built-in filtering interface:

- **Filter Input** - Type service names and press Enter
- **Quick Buttons** - Click for common service combinations
- **No Reloads** - Instant filtering without page refresh
- **Persistent** - Your filters are saved across sessions

## @expose Decorator (Enhanced!)

### **Basic Usage**

```python
from app.api_router import expose

@expose(
    path='/items',
    methods=['GET', 'POST'],
    summary='Manage items',
    description='CRUD operations for items',
    tags=['__SERVICE_NAME__', 'items'],
    status_codes={200: 'Success', 201: 'Created'}
)
def my_method(self, request):
    # Implementation
    pass
```

### **Direct Schema Definition** 🚀

```python
@expose(
    path='/items',
    methods=['POST'],
    tags=['Items'],
    request_schema={
        "type": "object",
        "properties": {
            "field": {"type": "string"},
            "optional_field": {"type": "string"}
        },
        "required": ["field"]
    },
    response_schema={
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "field": {"type": "string"},
            "optional_field": {"type": "string"}
        }
    }
)
```

## Special Tag Markers

- `__SERVICE_NAME__` → Replaced with actual service name
- `{service_name}` → Replaced with service name in title case

## Automatic Schema Generation

### **CRUD Services** (Automatic!)

CRUD services automatically generate schemas from models:

- **Create Schema** - Generated from model fields (excludes ID, timestamps)
- **Update Schema** - Generated from model fields (excludes ID, timestamps)
- **Response Schema** - Generated from model fields (includes all fields)

### **Custom Services** (Manual)

Custom services define schemas in `@expose` decorator:

```python
@expose(
    request_schema={"type": "object", "properties": {...}},
    response_schema={"type": "object", "properties": {...}}
)
```

## Error Handling

Errors are automatically caught and logged:

- Terminal output with emojis
- Structured JSON responses
- Full tracebacks in debug mode

## Key Endpoints

- `/api/openapi.json` - OpenAPI specification (filterable)
- `/api/docs` - Swagger UI interface

## Common Patterns

### **CRUD Service** (Automatic Schemas!)

```python
class ArtistService(CrudService):
    model = Artist
    config = {
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name']
        }
    }
    # Automatically gets Create/Update/Response schemas!
```

### **Custom Service** (Manual Schemas)

```python
class ChatService(BaseApiService):
    @expose(
        path='/sessions',
        methods=['POST'],
        tags=['Chat'],
        request_schema={
            "type": "object",
            "properties": {
                "persona_id": {"type": "integer"},
                "session_name": {"type": "string"}
            },
            "required": ["persona_id"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "persona_id": {"type": "integer"},
                "session_name": {"type": "string"}
            }
        }
    )
    def create_session(self, request):
        pass
```

## Troubleshooting

- **Service not showing**: Check `@expose` decorator
- **Schemas not working**: Use `request_schema`/`response_schema` in decorator
- **CRUD schemas missing**: Ensure service extends `CrudService` with model/config
- **Filtering not working**: Check query parameter format
- **Routes not working**: Verify blueprint registration

## Performance Tips

- Use service filtering to reduce OpenAPI spec size
- Keep services focused and lightweight
- Use appropriate HTTP methods and status codes
- CRUD services automatically optimize schema generation