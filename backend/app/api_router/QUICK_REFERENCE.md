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

### **NEW: Direct Schema Definition** 🚀
```python
@expose(
    path='/items',
    methods=['POST'],
    tags=['Items'],
    request_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Item name"},
            "description": {"type": "string", "description": "Item description"}
        },
        "required": ["name"]
    },
    response_schema={
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "description": {"type": "string"}
        }
    }
)
def create_item(self, request):
    pass
```

### **Legacy DTO Support** (Still Works)
```python
from pydantic import BaseModel

class CreateItemDTO(BaseModel):
    field: str
    optional_field: str | None = None

# Use in @expose decorator
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

- `