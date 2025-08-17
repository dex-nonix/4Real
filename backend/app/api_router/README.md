# API Router System Documentation

## Overview

The API Router system is a modular, auto-documenting Flask API framework that automatically generates OpenAPI 3.0 specifications and Swagger UI documentation. It provides a clean separation of concerns between routing, documentation generation, and service management.

**🚀 NEW: Enhanced Swagger Generation**
- **BaseApiService** - Base class for all services with automatic Swagger generation
- **CrudService** - Automatic schema generation from models and configs
- **Enhanced @expose** - Direct schema definition in decorators
- **No DTOs required** - Schemas defined directly or generated automatically

## Architecture

```
api_router/
├── __init__.py              # Package exports
├── api_router.py            # Core routing and service management
├── openapi_generator.py     # OpenAPI 3.0 specification generation
├── swagger_ui_generator.py  # Swagger UI HTML generation
├── documentation_router.py  # Documentation endpoint management
└── README.md               # This documentation

services/
├── base_api_service.py      # 🚀 NEW: Base class for all services
├── crud_service.py          # 🚀 ENHANCED: Automatic schema generation
└── [other services]         # Custom services with manual schemas
```

## Core Components

### 1. APIRouter (`api_router.py`)

The main router class that handles service registration, route creation, and request handling.

**Key Features:**
- Automatic service registration and route creation
- Built-in error handling and logging
- Service lifecycle management
- Blueprint integration with Flask

**Usage:**
```python
from app.api_router import APIRouter

# Create router instance
router = APIRouter()

# Register services
router.register_service('artists', ArtistService)
router.register_service('albums', AlbumService)

# Get the Flask blueprint
blueprint = router.blueprint
```

**Methods:**
- `register_service(service_name, service_class, *args, **kwargs)`: Register a service class
- `register_service_factory(service_name, factory)`: Register a service using a factory function
- `list_services()`: Get list of registered service names
- `get_service(service_name)`: Get a specific service instance

### 2. BaseApiService (`base_api_service.py`) 🚀 NEW!

Base class for all API services that provides automatic Swagger documentation generation.

**Key Features:**
- **Automatic Swagger generation** from `@expose` decorators
- **Default `method_to_swagger()`** implementation for all subclasses
- **No override required** for most services
- **Clean architecture** with separation of concerns

**Usage:**
```python
from app.services.base_api_service import BaseApiService

class MyService(BaseApiService):
    # Automatically gets to_swagger() method
    # Automatically gets method_to_swagger() method
    # No override needed for basic functionality
    
    @expose('/items', methods=['GET'], tags=['Items'])
    def list_items(self, request):
        return {'items': []}
```

### 3. CrudService (`crud_service.py`) 🚀 ENHANCED!

Enhanced CRUD service that automatically generates schemas from models and configurations.

**Key Features:**
- **Automatic schema generation** from SQLAlchemy models
- **Config-driven validation** and field requirements
- **Override of `method_to_swagger()`** for dynamic model schemas
- **Create/Update/Response schemas** generated automatically

**Usage:**
```python
from app.services.crud_service import CrudService

class ArtistService(CrudService):
    model = Artist  # Automatically generates schemas
    config = {
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name']
        },
        'filters': {
            'fields': ['name', 'abbreviation']
        }
    }
    # Automatically gets:
    # - ArtistServiceCreate schema
    # - ArtistServiceUpdate schema  
    # - ArtistServiceResponse schema
```

**Automatic Schema Generation:**
- **Create Schema**: Model fields excluding ID, timestamps
- **Update Schema**: Model fields excluding ID, timestamps  
- **Response Schema**: All model fields with proper types

### 4. OpenAPIGenerator (`openapi_generator.py`)

Handles the generation of OpenAPI 3.0 specifications from registered services.

**Key Features:**
- **Service-aware schema generation** via `to_swagger()` method
- **Automatic schema extraction** from `@expose` decorators
- **Dynamic tag processing**
- **Path parameter extraction**
- **Service filtering support**

**Service Integration:**
```python
# Generate spec for all services
spec = generator.generate_openapi_spec(services)

# Generate spec for specific services only
spec = generator.generate_openapi_spec(services, "chat,artists")

# Generate spec for a single service
spec = generator.generate_openapi_spec(services, "chat")
```

**Filter Format:**
- Comma-separated service names
- Case-insensitive matching
- Whitespace is automatically trimmed
- Examples: `"chat"`, `"chat,artists"`, `"chat, artists, albums"`

### 5. SwaggerUIGenerator (`swagger_ui_generator.py`)

Generates the Swagger UI HTML interface for API exploration with advanced service filtering.

**Features:**
- Modern Swagger UI 5.9.0
- **Service Filtering Interface** - Filter services without reloading
- **Quick Filter Buttons** - Pre-defined service combinations
- **Persistent State** - Remembers your filter preferences
- **Real-time Filtering** - Apply filters instantly
- Responsive design
- Deep linking support
- Download URL plugin

### 6. DocumentationRouter (`documentation_router.py`)

Manages documentation endpoints and integrates the OpenAPI and Swagger UI generators.

**Endpoints:**
- `/api/openapi.json` - OpenAPI specification (supports filtering)
- `/api/docs` - Swagger UI interface

## Service Registration

### **NEW: Service Architecture**

#### **BaseApiService** (All Services)
```python
from app.services.base_api_service import BaseApiService

class MyService(BaseApiService):
    # Automatically gets Swagger generation
    # No override needed for basic functionality
    pass
```

#### **CrudService** (CRUD Operations)
```python
from app.services.crud_service import CrudService

class ArtistService(CrudService):
    model = Artist  # Automatic schema generation
    config = {
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name']
        }
    }
    # Gets automatic Create/Update/Response schemas!
```

#### **Custom Services** (Special Logic)
```python
class ChatService(BaseApiService):
    # Can override method_to_swagger() if needed
    # Usually just uses @expose decorator for schemas
    pass
```

### Basic Service Registration

```python
from app.api_router import APIRouter

class MyService(BaseApiService):
    @expose(path='/items', methods=['GET'])
    def get_items(self, request):
        return {'items': []}

# Register the service
router = APIRouter()
router.register_service('my-service', MyService)
```

### Service with Direct Schemas 🚀 NEW!

```python
class MyService(BaseApiService):
    @expose(
        path='/items',
        methods=['POST'],
        summary='Create a new item',
        description='Creates a new item with the provided details',
        tags=['__SERVICE_NAME__', 'items'],
        # 🚀 NEW: Direct schema definition
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
        },
        status_codes={200: 'Success', 201: 'Created'}
    )
    def create_item(self, request):
        # Implementation here
        pass
```

### **Legacy DTO Support (Still Works)**

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

## API Documentation Features

### **NEW: Enhanced Schema Generation**

#### **Automatic CRUD Schemas**
CRUD services automatically generate schemas from models:

```python
class ArtistService(CrudService):
    model = Artist
    config = {
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name']
        }
    }
    
    # Automatically gets:
    # - ArtistServiceCreate: {name: string, abbreviation: string, persona: string}
    # - ArtistServiceUpdate: {name: string, abbreviation: string, persona: string}  
    # - ArtistServiceResponse: {id: integer, name: string, abbreviation: string, persona: string, created_at: string, updated_at: string}
```

#### **Manual Schema Definition**
Custom services define schemas in `@expose` decorator:

```python
@expose(
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
```

### Dynamic Service Filtering

The OpenAPI endpoint now supports query parameter filtering, and the Swagger UI provides an intuitive interface for this:

#### **Backend Filtering (Query Parameters)**
```
# All services
GET /api/openapi.json

# Only chat service
GET /api/openapi.json?services=chat

# Multiple services
GET /api/openapi.json?services=chat,artists,albums

# Services with spaces (automatically handled)
GET /api/openapi.json?services=chat, artists , albums
```

#### **Frontend Filtering (Swagger UI)**
The Swagger UI now includes:
- **Filter Input Field** - Type service names and press Enter or click Apply
- **Quick Filter Buttons** - One-click access to common service combinations
- **Real-time Updates** - No page reloads, instant filtering
- **Persistent State** - Your filter preferences are saved across sessions
- **Current Filter Display** - Shows what's currently being filtered

### Tag Processing

The system automatically processes tags with special markers:

- `__SERVICE_NAME__` → Replaced with the actual service name
- `{service_name}` → Replaced with the service name in title case

**Examples:**
```python
@expose(tags=['__SERVICE_NAME__', 'core'])  # → ['Chat', 'core']
@expose(tags=['{service_name}-operations']) # → ['Chat-operations']
```

## Error Handling

The API router includes comprehensive error handling:

- Automatic exception catching and logging
- Structured error responses
- Debug mode support for tracebacks
- Terminal output for immediate debugging

**Error Response Format:**
```json
{
  "error": "Service Error",
  "service": "service_name",
  "method": "method_name",
  "message": "Error description",
  "traceback": "Full traceback (in debug mode)"
}
```

## Logging

The system provides detailed logging:

- Service execution logging
- Error logging with full tracebacks
- Request/response logging
- Performance monitoring

**Log Format:**
```
🚀 Executing service_name.method_name with kwargs: {...}
✅ Successfully executed service_name.method_name
💥 CRASH in service_name.method_name: Error message
```

## Configuration

### Flask Integration

```python
from flask import Flask
from app.api_router import APIRouter

app = Flask(__name__)
router = APIRouter()

# Register the API blueprint
app.register_blueprint(router.blueprint, url_prefix='/api')
```

### Environment Variables

No specific environment variables are required, but the system respects Flask's configuration:

- `DEBUG`: Enables detailed error responses
- `UPLOAD_DIR`: Directory for file uploads

## Best Practices

### 1. Service Organization

- **Use BaseApiService** for all services
- **Extend CrudService** for CRUD operations
- **Keep services focused** on single domains
- **Use descriptive service names**

### 2. Schema Definition

- **CRUD services**: Let automatic generation handle schemas
- **Custom services**: Use `request_schema`/`response_schema` in decorator
- **Legacy support**: DTOs still work if needed
- **Always provide meaningful** summaries and descriptions

### 3. Documentation

- **Use appropriate tags** for grouping
- **Include request/response schemas** for complex operations
- **CRUD services**: Schemas generated automatically
- **Custom services**: Define schemas in decorator

### 4. Error Handling

- Let the router handle common errors
- Provide meaningful error messages in your services
- Use appropriate HTTP status codes

### 5. Performance

- Use service filtering to reduce OpenAPI spec size
- Implement caching for expensive operations
- Monitor service execution times
- CRUD services automatically optimize schema generation

## Examples

### Complete CRUD Service Example 🚀 NEW!

```python
from app.services.crud_service import CrudService

class ArtistService(CrudService):
    model = Artist
    config = {
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name']
        },
        'filters': {
            'fields': ['name', 'abbreviation']
        },
        'sorting': {
            'default_sort': 'name',
            'allowed_fields': ['name', 'abbreviation', 'created_at']
        }
    }
    
    # 🚀 Automatically gets:
    # - Create schema (excludes id, created_at, updated_at)
    # - Update schema (excludes id, created_at, updated_at)  
    # - Response schema (includes all fields)
    # - All CRUD operations with proper schemas
```

### Complete Custom Service Example

```python
from app.services.base_api_service import BaseApiService

class ChatService(BaseApiService):
    @expose(
        path='/sessions',
        methods=['POST'],
        summary='Create chat session',
        description='Create a new chat session with a persona',
        tags=['Chat', 'Sessions'],
        status_codes={201: 'Session created', 400: 'Bad request'},
        # 🚀 Direct schema definition
        request_schema={
            "type": "object",
            "properties": {
                "persona_id": {"type": "integer", "description": "Persona ID"},
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"}
            },
            "required": ["persona_id"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "persona_id": {"type": "integer"},
                "session_name": {"type": "string"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        }
    )
    def create_session(self, request):
        # Implementation here
        pass
```

### Registration

```python
from app.api_router import APIRouter

router = APIRouter()
router.register_service('artists', ArtistService)  # CRUD service
router.register_service('chat', ChatService)       # Custom service
```

## Troubleshooting

### Common Issues

1. **Service not appearing in OpenAPI spec**
   - Check that methods have `@expose` decorator
   - Verify service extends `BaseApiService`
   - Check for import errors

2. **CRUD schemas not appearing**
   - Ensure service extends `CrudService`
   - Verify `model` and `config` are properly set
   - Check that model has proper SQLAlchemy fields

3. **Custom schemas not working**
   - Use `request_schema`/`response_schema` in `@expose` decorator
   - Ensure schemas follow OpenAPI 3.0 format
   - Check for syntax errors in schema definitions

4. **Routes not working**
   - Check Flask blueprint registration
   - Verify URL prefix configuration
   - Check for route conflicts

5. **Filtering not working**
   - Verify query parameter format (`?services=name1,name2`)
   - Check service names match exactly (case-insensitive)
   - Ensure no extra spaces in parameter values

### Debug Mode

Enable Flask debug mode for detailed error information:

```python
app.config['DEBUG'] = True
```

## Migration Guide

### From Old System to New System

1. **Update service inheritance**:
   ```python
   # OLD
   class MyService:
       pass
   
   # NEW
   from app.services.base_api_service import BaseApiService
   class MyService(BaseApiService):
       pass
   ```

2. **Update CRUD services**:
   ```python
   # OLD
   class ArtistService:
       pass
   
   # NEW
   from app.services.crud_service import CrudService
   class ArtistService(CrudService):
       model = Artist
       config = {...}
   ```

3. **Update schema definitions**:
   ```python
   # OLD (DTOs)
   @expose(request_dto=MyDTO, response_dto=MyDTO)
   
   # NEW (Direct schemas)
   @expose(
       path='/items',
       methods=['POST'],
       tags=['Items'],
       request_schema={
           "type": "object",
           "properties": {
               "name": {"type": "string"},
               "description": {"type": "string"}
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
   ```

## Future Enhancements

Planned features for upcoming versions:

- Service grouping and categorization
- Advanced filtering options (exclude services, tag-based filtering)
- Performance metrics and monitoring
- Service dependency visualization
- Custom documentation themes
- API versioning support
- Rate limiting integration
- Authentication/authorization hooks
- **Enhanced schema validation** and generation
- **Model relationship schemas** for CRUD services

## Contributing

When contributing to the API router system:

1. Maintain separation of concerns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Follow the existing code style and patterns
5. Ensure backward compatibility
6. **Use BaseApiService** for new services
7. **Extend CrudService** for CRUD operations
8. **Define schemas in decorators** for custom services

## License

This API router system is part of the 4Real project and follows the project's licensing terms.
