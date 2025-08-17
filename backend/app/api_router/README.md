# API Router System Documentation

## Overview

The API Router system is a modular, auto-documenting Flask API framework that automatically generates OpenAPI 3.0 specifications and Swagger UI documentation. It provides a clean separation of concerns between routing, documentation generation, and service management.

## Architecture

```
api_router/
├── __init__.py              # Package exports
├── api_router.py            # Core routing and service management
├── openapi_generator.py     # OpenAPI 3.0 specification generation
├── swagger_ui_generator.py  # Swagger UI HTML generation
├── documentation_router.py  # Documentation endpoint management
└── README.md               # This documentation
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

### 2. OpenAPIGenerator (`openapi_generator.py`)

Handles the generation of OpenAPI 3.0 specifications from registered services.

**Key Features:**
- Automatic schema extraction from DTOs
- Dynamic tag processing
- Path parameter extraction
- Service filtering support

**Service Filtering:**
The OpenAPI generator now supports filtering services by name:

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

### 3. SwaggerUIGenerator (`swagger_ui_generator.py`)

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

### 4. DocumentationRouter (`documentation_router.py`)

Manages documentation endpoints and integrates the OpenAPI and Swagger UI generators.

**Endpoints:**
- `/api/openapi.json` - OpenAPI specification (supports filtering)
- `/api/docs` - Swagger UI interface

## Service Registration

### Basic Service Registration

```python
from app.api_router import APIRouter

class MyService:
    @expose(path='/items', methods=['GET'])
    def get_items(self, request):
        return {'items': []}

# Register the service
router = APIRouter()
router.register_service('my-service', MyService)
```

### Service with DTOs

```python
from pydantic import BaseModel

class CreateItemDTO(BaseModel):
    name: str
    description: str

class ItemResponseDTO(BaseModel):
    id: int
    name: str
    description: str

class MyService:
    @expose(
        path='/items',
        methods=['POST'],
        request_dto=CreateItemDTO,
        response_dto=ItemResponseDTO,
        summary='Create a new item',
        description='Creates a new item with the provided details',
        tags=['__SERVICE_NAME__', 'items']
    )
    def create_item(self, request):
        # Implementation here
        pass
```

## API Documentation Features

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

### Automatic Schema Generation

DTOs are automatically included in the OpenAPI specification:

- Request DTOs appear in request body schemas
- Response DTOs appear in response schemas
- All schemas are properly referenced and documented

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

- Use descriptive service names
- Group related functionality in single services
- Keep services focused on single domains

### 2. Documentation

- Always provide meaningful summaries and descriptions
- Use appropriate tags for grouping
- Include request/response DTOs for complex operations

### 3. Error Handling

- Let the router handle common errors
- Provide meaningful error messages in your services
- Use appropriate HTTP status codes

### 4. Performance

- Use service filtering to reduce OpenAPI spec size
- Implement caching for expensive operations
- Monitor service execution times

## Examples

### Complete Service Example

```python
from app.api_router import expose
from pydantic import BaseModel

class UserCreateDTO(BaseModel):
    username: str
    email: str

class UserResponseDTO(BaseModel):
    id: int
    username: str
    email: str

class UserService:
    def __init__(self):
        self.users = []
        self.next_id = 1

    @expose(
        path='/users',
        methods=['GET'],
        summary='List all users',
        description='Retrieve a list of all registered users',
        tags=['__SERVICE_NAME__', 'users'],
        response_dto=UserResponseDTO
    )
    def list_users(self, request):
        return [UserResponseDTO(**user) for user in self.users]

    @expose(
        path='/users',
        methods=['POST'],
        summary='Create user',
        description='Create a new user account',
        tags=['__SERVICE_NAME__', 'users'],
        request_dto=UserCreateDTO,
        response_dto=UserResponseDTO,
        status_codes={201: 'User created successfully'}
    )
    def create_user(self, request):
        data = request.get_json()
        user = {
            'id': self.next_id,
            'username': data['username'],
            'email': data['email']
        }
        self.users.append(user)
        self.next_id += 1
        return UserResponseDTO(**user), 201
```

### Registration

```python
from app.api_router import APIRouter

router = APIRouter()
router.register_service('users', UserService)
```

## Troubleshooting

### Common Issues

1. **Service not appearing in OpenAPI spec**
   - Check that methods have `@expose` decorator
   - Verify service is properly registered
   - Check for import errors

2. **DTO schemas not appearing**
   - Ensure DTOs inherit from `pydantic.BaseModel`
   - Check that `request_dto` and `response_dto` are properly set
   - Verify DTO import paths

3. **Routes not working**
   - Check Flask blueprint registration
   - Verify URL prefix configuration
   - Check for route conflicts

4. **Filtering not working**
   - Verify query parameter format (`?services=name1,name2`)
   - Check service names match exactly (case-insensitive)
   - Ensure no extra spaces in parameter values

### Debug Mode

Enable Flask debug mode for detailed error information:

```python
app.config['DEBUG'] = True
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

## Contributing

When contributing to the API router system:

1. Maintain separation of concerns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Follow the existing code style and patterns
5. Ensure backward compatibility

## License

This API router system is part of the 4Real project and follows the project's licensing terms.
