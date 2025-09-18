# Nonix Database Plugin - Usage Guide

## Overview

The Nonix Database Plugin provides a comprehensive, production-ready database foundation for the unified Nonix ecosystem. Built with AI-first principles and maximum extensibility, it leverages Python's lazy loading capabilities to serve as a generic base that powers web, GUI, CLI, and AI interfaces through clean abstractions. It handles database engine management, session lifecycle, automatic table creation, and provides a sophisticated CRUD (Create, Read, Update, Delete) system with advanced filtering, sorting, pagination, and validation capabilities.

**⚠️ Important Notes**:
- This is a **fundamental plugin** that serves as the database foundation for the entire Nonix ecosystem
- The CRUD system provides enterprise-grade database operations with comprehensive configuration options
- Provides async SQLAlchemy integration with session management and automatic table creation
- Designed as part of the unified Nonix system where web components serve as a generic base that other interfaces (GUI, CLI, AI) can build upon through lazy loading

## Dependencies

### Core Plugin System
- **Plugin System**: For plugin lifecycle management
- **DI System**: For session injection and service registration

### Database Dependencies
- **SQLAlchemy**: Async SQLAlchemy for database operations
- **aiosqlite/sqlite3**: Default SQLite support (easily configurable for PostgreSQL, MySQL, etc.)

## Architecture

### Core Components
- **NxWebDbPlugin**: Main plugin that manages database engine and sessions
- **Base Models**: Abstract base classes with automatic timestamps
- **CRUD System**: Comprehensive Create/Read/Update/Delete operations
- **Session Management**: Async session lifecycle with FastAPI integration

### Data Flow
1. **Plugin loads** → Initializes database engine and creates tables
2. **Application starts** → Session factory becomes available via DI
3. **Services inject sessions** → Database operations use managed sessions
4. **CRUD operations** → Advanced querying with filtering/sorting/pagination

### Unified System Integration
The database plugin is designed as part of the unified Nonix system where:
- **Web components serve as base** → Other interfaces (GUI, CLI, AI) build upon them through lazy loading
- **Clean abstractions** → Interfaces and base classes allow seamless integration
- **AI-first design** → Everything from ground up designed to work with AI plugins
- **Maximum extensibility** → Super slim, super fast, extendable architecture
- **No redundancy** → Single implementation serves all interface types

## Quick Start

### 1. Add Database Plugin

The database plugin is typically a core dependency:

```python
settings.PLUGINS = [
    {"name": "db"},  # Database plugin (fundamental)
    # ... other plugins that depend on database
]
```

### 2. Configure Database Connection

Configure your database connection in the plugin settings:

```json
{
  "name": "db",
  "config": {
    "url": "sqlite+aiosqlite:///./myapp.db",
    "options": {
      "echo": false,
      "pool_pre_ping": true
    }
  }
}
```

### 3. Use Database Sessions

Inject database sessions in your services:

```python
from nonix_di.resolve import NxInject
from nonix_web_db import AsyncSessionLocal

class MyService:
    async def get_data(self):
        async with AsyncSessionLocal() as session:
            # Use session for database operations
            result = await session.execute(select(MyModel))
            return result.scalars().all()
```

### 4. Define Your Models

Create models inheriting from the base classes:

```python
from sqlalchemy import Column, String, Integer
from nonix_web_db import Base

class User(Base):
    __tablename__ = 'users'

    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    age = Column(Integer)
```

## Model Definitions

### Base Model Classes

The plugin provides two fundamental base classes:

#### Base
```python
from nonix_web_db import Base

class MyModel(Base):
    __tablename__ = 'my_models'
    # Your fields here
```

#### BaseModel (Recommended)
```python
from nonix_web_db import BaseModel

class MyModel(BaseModel):
    __tablename__ = 'my_models'

    name = Column(String(100))
    description = Column(String(500))

    # Automatic fields provided:
    # - id: Primary key (Integer, auto-increment)
    # - created_at: Creation timestamp
    # - updated_at: Last update timestamp
```

### Model Features

BaseModel provides:
- **Automatic Timestamps**: `created_at` and `updated_at` fields
- **to_dict() Method**: Convert model instances to dictionaries
- **Smart __repr__**: Intelligent string representation
- **JSON Serialization**: Proper datetime handling

## Session Management

### Async Session Factory

The plugin provides a global async session factory:

```python
from nonix_web_db import AsyncSessionLocal

# Use in async context
async def my_function():
    async with AsyncSessionLocal() as session:
        # Database operations here
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
```

### FastAPI Integration

For web applications, the plugin provides FastAPI dependency injection:

```python
from fastapi import Depends
from nonix_web_db import get_db

@app.get("/users")
async def get_users(db = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Manual Session Management

For complex scenarios, manage sessions manually:

```python
from nonix_web_db.plugin import AsyncSessionLocal

async def complex_operation():
    session = AsyncSessionLocal()
    try:
        async with session.begin():
            # Multiple operations in transaction
            user = User(name="John", email="john@example.com")
            session.add(user)

            profile = UserProfile(user_id=user.id, bio="Hello!")
            session.add(profile)

        await session.commit()
    except Exception as e:
        await session.rollback()
        raise
    finally:
        await session.close()
```

## CRUD Operations

### Basic CRUD Service

Create services that inherit from BaseCrudService:

```python
from nonix_web_db.crud import BaseCrudService, CRUDConfig
from .models import User
from .schemas import UserCreate, UserUpdate, UserResponse

class UserService(BaseCrudService):
    config = CRUDConfig(
        model=User,
        create_schema=UserCreate,
        update_schema=UserUpdate,
        response_schema=UserResponse
    )

    # Service is now ready with full CRUD operations
```

### Advanced CRUD Configuration

Configure filtering, sorting, pagination, and validation:

```python
from nonix_web_db.crud import (
    CRUDConfig, FilterConfig, SortingConfig,
    ValidationConfig, PaginationConfig, SelectorConfig
)

class AdvancedUserService(BaseCrudService):
    config = CRUDConfig(
        model=User,
        create_schema=UserCreate,
        update_schema=UserUpdate,
        response_schema=UserResponse,

        # Configure filtering
        filters=FilterConfig(
            allowed_fields=['name', 'email', 'age'],
            search_fields=['name', 'email']
        ),

        # Configure sorting
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'email', 'created_at']
        ),

        # Configure validation
        validation=ValidationConfig(
            unique_fields=['email']
        ),

        # Configure pagination
        pagination=PaginationConfig(
            default_page_size=20,
            max_page_size=100
        ),

        # Configure selector/dropdown
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name} ({email})',
            search_fields=['name', 'email']
        )
    )
```

## CRUD Operations Usage

### Create Records

```python
user_data = UserCreate(name="John Doe", email="john@example.com")
user = await user_service.create(user_data)
```

### Read Operations

```python
# Get single record
user = await user_service.get_one(user_id=1)

# Get all with pagination and filtering
result = await user_service.get_all({
    'page': 1,
    'per_page': 20,
    'filter_name': 'John',
    'order_by': 'created_at:desc'
})

# Search records
search_result = await user_service.search({
    'page': 1,
    'per_page': 10
}, "john")
```

### Update Records

```python
update_data = UserUpdate(name="Jane Doe")
updated_user = await user_service.update(user_id=1, update_data)
```

### Delete Records

```python
await user_service.delete(user_id=1)
```

### Advanced Filtering

The CRUD system supports sophisticated filtering:

```python
# Field-based filtering
result = await user_service.get_all({
    'filter_name': 'John',           # Exact match
    'filter_age': 'gt:25',           # Greater than
    'filter_created_at': 'gte:2024-01-01T00:00:00',  # Date range
    'filter_email': 'like:%@gmail.com'  # Pattern matching
})

# Multiple filters
result = await user_service.get_all({
    'filter_age': 'gte:18',
    'filter_age': 'lte:65',
    'filter_active': 'true'
})
```

### Bulk Operations

```python
# Bulk update
await user_service.bulk_update(
    ids=[1, 2, 3],
    data={'active': False}
)

# Bulk delete (if configured)
await user_service.bulk_delete(ids=[1, 2, 3])
```

### Selector/Dropdown Support

```python
# Get selector data for dropdowns
options = await user_service.selector(query="john")

# Returns format:
# [
#     {"id": 1, "value": 1, "label": "John Doe (john@example.com)"},
#     {"id": 2, "value": 2, "label": "Johnny Smith (johnny@example.com)"}
# ]

# Get single selector item
option = await user_service.single_selector(user_id=1)
```

## Configuration Options

### Database Engine Configuration

```json
{
  "name": "db",
  "config": {
    "url": "postgresql+asyncpg://user:pass@localhost/dbname",
    "options": {
      "echo": false,
      "pool_size": 10,
      "max_overflow": 20,
      "pool_pre_ping": true,
      "pool_recycle": 3600
    }
  }
}
```

### Supported Databases

- **SQLite**: `sqlite+aiosqlite:///database.db`
- **PostgreSQL**: `postgresql+asyncpg://user:pass@host/db`
- **MySQL**: `mysql+aiomysql://user:pass@host/db`
- **Oracle**: `oracle+oracledb://user:pass@host/db`

## Advanced Features

### Context-Aware Filtering

Services can automatically filter based on context:

```python
class TenantUserService(BaseCrudService):
    config = CRUDConfig(
        model=User,
        filters=FilterConfig(
            context_aware=True,
            auto_filters={
                'tenant_id': 'tenant_id'  # Map context key to model field
            }
        )
    )

# Context is automatically applied to all queries
users = await tenant_user_service.get_all({
    'context': {'tenant_id': 123}
})
```

### Default Filters

Apply default filters to all queries:

```python
class ActiveUserService(BaseCrudService):
    config = CRUDConfig(
        model=User,
        filters=FilterConfig(
            default_filters={
                'active': True,           # Static default
                'tenant_id': 'required'   # Required from context
            }
        )
    )
```

### Custom Validation

Implement custom validation logic:

```python
class ValidatedUserService(BaseCrudService):
    config = CRUDConfig(
        model=User,
        validation=ValidationConfig(
            unique_fields=['email', 'username']
        )
    )

    async def _validate_unique_fields(self, data, item_id, session):
        # Custom validation logic
        await super()._validate_unique_fields(data, item_id, session)

        # Additional custom validation
        if hasattr(data, 'age') and data.age < 13:
            raise HTTPException(
                status_code=400,
                detail="Users must be at least 13 years old"
            )
```

## Migration and Schema Management

### Automatic Table Creation

The plugin automatically creates tables on startup:

```python
# Tables are created automatically when plugin starts
# No manual migration scripts needed for simple schemas
```

### Manual Schema Management

For complex migrations, use Alembic:

```python
# alembic.ini
[alembic]
script_location = migrations

# Generate migration
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head
```

## Performance Optimization

### Connection Pooling

Configure connection pooling for production:

```json
{
  "name": "db",
  "config": {
    "options": {
      "pool_size": 10,
      "max_overflow": 20,
      "pool_pre_ping": true,
      "pool_recycle": 3600,
      "echo": false
    }
  }
}
```

### Query Optimization

Use efficient querying patterns:

```python
# Efficient pagination
result = await user_service.get_all({
    'page': 1,
    'per_page': 50,
    'order_by': 'id'  # Use indexed field
})

# Selective field loading
users = await session.execute(
    select(User.id, User.name).where(User.active == True)
)
```

### Caching Strategies

Implement caching for frequently accessed data:

```python
from functools import lru_cache
import asyncio

class CachedUserService(BaseCrudService):
    @lru_cache(maxsize=1000)
    def _get_user_cache_key(self, user_id: int) -> str:
        return f"user:{user_id}"

    async def get_cached_user(self, user_id: int):
        cache_key = self._get_user_cache_key(user_id)

        # Check cache first
        cached_user = await self._get_from_cache(cache_key)
        if cached_user:
            return cached_user

        # Fetch from database
        user = await self.get_one(user_id)

        # Cache result
        await self._set_cache(cache_key, user, ttl=300)
        return user
```

## Monitoring and Observability

### Query Logging

Enable query logging for debugging:

```json
{
  "name": "db",
  "config": {
    "options": {
      "echo": true
    }
  }
}
```

### Performance Metrics

Monitor database performance:

```python
import time
from nonix_web_db import AsyncSessionLocal

class DatabaseMonitor:
    async def measure_query_time(self, query):
        start_time = time.time()

        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
            data = result.scalars().all()

        duration = time.time() - start_time
        print(f"Query took {duration:.3f} seconds")

        return data
```

### Connection Health Checks

Monitor database connectivity:

```python
from sqlalchemy import text

class HealthCheckService:
    async def check_database_health(self):
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "database": str(e)}
```

## Troubleshooting

### Connection Issues

**Problem**: Database connection fails

**Solutions**:
- Verify database URL format
- Check database server is running
- Ensure correct credentials
- Test network connectivity

### Migration Issues

**Problem**: Schema changes not applied

**Solutions**:
- Run database migrations manually
- Check migration scripts are up to date
- Verify model definitions match database schema
- Use `echo: true` for detailed query logging

### Performance Issues

**Problem**: Slow database queries

**Solutions**:
- Add database indexes on frequently queried fields
- Optimize query patterns (avoid N+1 queries)
- Implement query result caching
- Monitor query execution plans

### Memory Issues

**Problem**: Memory usage grows over time

**Solutions**:
- Configure appropriate connection pool sizes
- Implement proper session cleanup
- Use streaming for large result sets
- Monitor for connection leaks

## Best Practices

### Model Design

```python
# ✅ Good: Use BaseModel for automatic timestamps
class Article(BaseModel):
    __tablename__ = 'articles'

    title = Column(String(200), nullable=False)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey('users.id'))

# ✅ Good: Add indexes for performance
class Article(BaseModel):
    __tablename__ = 'articles'

    title = Column(String(200), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), index=True)
```

### Service Organization

```python
# ✅ Good: Separate concerns
class UserRepository(BaseCrudService):
    # Data access only
    pass

class UserService:
    def __init__(self):
        self.repository = NxInject(UserRepository)

    async def create_user(self, user_data):
        # Business logic here
        # Validation, transformation, etc.
        return await self.repository.create(user_data)
```

### Error Handling

```python
# ✅ Good: Comprehensive error handling
class RobustUserService(BaseCrudService):
    async def create_user(self, user_data):
        try:
            # Validate business rules
            await self._validate_business_rules(user_data)

            # Create user
            user = await self.create(user_data)

            # Send welcome email
            await self._send_welcome_email(user)

            return user

        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            raise HTTPException(status_code=500, detail="User creation failed")
```

### Transaction Management

```python
# ✅ Good: Use transactions for data consistency
async def transfer_funds(self, from_user_id, to_user_id, amount):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Debit from sender
            await session.execute(
                update(User).where(User.id == from_user_id)
                .values(balance=User.balance - amount)
            )

            # Credit to receiver
            await session.execute(
                update(User).where(User.id == to_user_id)
                .values(balance=User.balance + amount)
            )

        await session.commit()
```


## Key Principles

### Unified Nonix System
- **Single implementation** = Serves web, GUI, CLI, and AI through lazy loading
- **Clean abstractions** = Interfaces allow seamless integration across all interfaces
- **AI-first design** = Built from ground up for AI plugin interactions
- **Maximum efficiency** = Super slim, super fast, highly extensible architecture

### Database as Foundation
- **Database plugin** = Fundamental data persistence layer for entire ecosystem
- **CRUD system** = Enterprise-grade data operations
- **Session management** = Reliable connection handling across all interfaces

### Service Architecture
- **Repositories** = Data access layer (inherit from BaseCrudService)
- **Services** = Business logic layer (inject repositories)
- **Dependency injection** = Clean separation of concerns

### Configuration-Driven
- **CRUDConfig** = Single source of truth for service configuration
- **Flexible filtering** = Context-aware and field-based filtering
- **Extensible validation** = Custom validation rules

**Remember**: The database plugin is the foundation of the unified Nonix ecosystem. Its comprehensive CRUD system and flexible configuration serve the entire system - from web interfaces to GUI applications to AI plugins - through clean abstractions and lazy loading. This ensures maximum efficiency with no redundant implementations across different interface types.

## Plugin Development Workflow

1. **Choose Database** - Select appropriate database for your needs
2. **Configure Plugin** - Set up database connection and options
3. **Define Models** - Create SQLAlchemy models inheriting from Base/BaseModel
4. **Create Services** - Implement CRUD services with appropriate configuration
5. **Configure CRUD** - Set up filtering, sorting, validation, and pagination
6. **Test Operations** - Verify create, read, update, delete operations work correctly
7. **Optimize Performance** - Add indexes, configure connection pooling, implement caching
8. **Monitor Health** - Set up health checks and performance monitoring

The database plugin provides a solid, scalable foundation for data persistence that grows with your application's needs while maintaining clean, maintainable code through its comprehensive configuration system.
