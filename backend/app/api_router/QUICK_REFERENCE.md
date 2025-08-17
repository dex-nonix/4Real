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

## Service Filtering (New Feature!)

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

## @expose Decorator

```python
from app.api_router import expose

@expose(
    path='/items',
    methods=['GET', 'POST'],
    summary='Manage items',
    description='CRUD operations for items',
    tags=['__SERVICE_NAME__', 'items'],
    request_dto=CreateItemDTO,
    response_dto=ItemResponseDTO,
    status_codes={200: 'Success', 201: 'Created'}
)
def my_method(self, request):
    # Implementation
    pass
```

## Special Tag Markers

- `__SERVICE_NAME__` → Replaced with actual service name
- `{service_name}` → Replaced with service name in title case

## DTOs (Data Transfer Objects)

```python
from pydantic import BaseModel

class MyDTO(BaseModel):
    field: str
    optional_field: str | None = None

# Use in @expose decorator
@expose(
    request_dto=MyDTO,
    response_dto=MyDTO
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

### Basic CRUD Service
```python
class MyService:
    @expose(path='/items', methods=['GET'])
    def list_items(self, request):
        return {'items': []}
    
    @expose(path='/items', methods=['POST'])
    def create_item(self, request):
        return {'id': 1, 'created': True}
    
    @expose(path='/items/<int:id>', methods=['GET'])
    def get_item(self, request, id):
        return {'id': id}
```

### Service with DTOs
```python
class CreateDTO(BaseModel):
    name: str

class ResponseDTO(BaseModel):
    id: int
    name: str

@expose(
    path='/items',
    methods=['POST'],
    request_dto=CreateDTO,
    response_dto=ResponseDTO
)
def create(self, request):
    pass
```

## Troubleshooting

- **Service not showing**: Check `@expose` decorator
- **DTOs not working**: Ensure inheritance from `pydantic.BaseModel`
- **Filtering not working**: Check query parameter format
- **Routes not working**: Verify blueprint registration

## Performance Tips

- Use service filtering to reduce OpenAPI spec size
- Keep services focused and lightweight
- Use appropriate HTTP methods and status codes
