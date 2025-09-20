# AI_README: Nonix Database Plugin API

## Requirements
- Python 3.8+
- sqlalchemy
- fastapi
- nonix_web
- nonix_plugin
- nonix_di

## Core Classes & Interfaces

### Database Plugin
```python
class NxWebDbPlugin(BasePlugin):
    """Database engine and session management plugin"""
    def __init__(self, config: Dict[str, Any]) -> None
    def _configure(self, config: Dict[str, Any]) -> None: """Configure database connection"""
    async def _startup(self, config: Dict[str, Any]) -> None: """Initialize database engine and create tables"""
    async def _shutdown(self, config: Dict[str, Any]) -> None: """Dispose database engine"""
    # Public attributes
    engine: AsyncEngine
```

### CRUD Router
```python
class NxWebServerCrudRouter(NxWebServerRouter):
    """Automatic REST API router for database models"""
    def __init__(self, router: APIRouter) -> None
    def _init_components(self) -> None: """Initialize query processor and routes"""
    def _register_routes(self) -> None: """Register CRUD endpoint routes"""
    # Public attributes
    service: BaseCrudService
    query_processor: QueryProcessor
```

### Base CRUD Service
```python
class BaseCrudService:
    """Base class for database CRUD operations"""
    def __init__(self) -> None
    async def create(self, data) -> Any: """Create new record"""
    async def get_one(self, id: int) -> Any: """Get single record by ID"""
    async def get_all(self, params: dict) -> PaginatedResponse: """Get paginated records"""
    async def update(self, id: int, data) -> Any: """Update record by ID"""
    async def delete(self, id: int) -> None: """Delete record by ID"""
    async def search(self, params: dict, query: str) -> PaginatedResponse: """Search records"""
    async def bulk_update(self, ids: list, data) -> dict: """Bulk update multiple records"""
    async def selector(self, query: str = None) -> list: """Get selector items"""
    async def single_selector(self, id: int) -> SelectorItem: """Get single selector item"""
    # Public attributes
    config: CRUDConfig
```

### Database Session
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""

def AsyncSessionLocal() -> async_sessionmaker:
    """Get configured async session factory"""
```

## Configuration Classes
```python
@dataclass
class CRUDConfig:
    """CRUD operation configuration"""
    model: Type
    create_schema: Type
    update_schema: Type
    response_schema: Type
    operations: CRUDOperations
    filters: FilterConfig
    sorting: SortingConfig
    validation: ValidationConfig
    selector: SelectorConfig

@dataclass
class FilterConfig:
    """Filtering configuration"""
    allowed_fields: List[str]

@dataclass
class SortingConfig:
    """Sorting configuration"""
    default_sort: str
    allowed_fields: List[str]

@dataclass
class ValidationConfig:
    """Validation configuration"""
    unique_fields: List[str]

@dataclass
class SelectorConfig:
    """Selector configuration"""
    fields: List[str]
    display_format: str
    search_fields: List[str]
```

## Integration Points
```python
# Enable database plugin
settings.PLUGINS = [
    {"name": "web_db", "config": {"url": "sqlite:///./app.db"}}
]

# Create CRUD service
class UserService(BaseCrudService):
    config = CRUDConfig(
        model=User,
        create_schema=UserCreate,
        update_schema=UserUpdate,
        response_schema=UserResponse,
        filters=FilterConfig(allowed_fields=["name", "email"]),
        sorting=SortingConfig(default_sort="name", allowed_fields=["name", "created_at"]),
        validation=ValidationConfig(unique_fields=["email"]),
        selector=SelectorConfig(fields=["name"], display_format="{name}", search_fields=["name"])
    )

# Register service and create router
@injectables([UserService])
@web_routers([UserRouter])
class DatabasePlugin(BasePlugin):
    pass

# Use in router
@router("/users", tags=["Users"])
class UserRouter(NxWebServerCrudRouter):
    service: UserService = NxInject(UserService)

# Database session dependency
from nonix_web_db import get_db

@route("/custom")
async def custom_endpoint(db: AsyncSession = Depends(get_db)):
    # Use db session
    pass
```

## Configuration Schema
```json
{
  "name": "web_db",
  "version": "1.0.0",
  "class": "NxWebDbPlugin",
  "dependencies": [],
  "config": {
    "url": "sqlite:///./app.db",
    "options": {
      "echo": false,
      "pool_size": 10,
      "max_overflow": 20
    }
  }
}
```
