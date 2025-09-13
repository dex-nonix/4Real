# NONIX PLUGIN SYSTEM - COMPLETE GUIDE

## Overview

The Nonix plugin system provides a modular architecture for extending both backend and frontend functionality. This document outlines the correct patterns and conventions to prevent architectural mistakes.

## Backend Plugin Architecture

### Plugin Structure

Every backend plugin must follow this exact structure:

```
nonix_[plugin_name]/
├── plugin.json          # Plugin metadata and configuration
├── plugin.py           # Main plugin class with decorators
├── models/             # Database models (if needed)
├── services/           # Business logic services
├── routers/            # API endpoints
└── __init__.py
```

### Plugin Metadata (plugin.json)

**REQUIRED FORMAT:**
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "class": "NxWebPluginNamePlugin",
  "dependencies": ["db"],
  "config": {
    "setting1": "value1",
    "setting2": "value2"
  }
}
```

**Rules:**
- `name`: kebab-case, matches directory name
- `class`: PascalCase, matches plugin class name
- `dependencies`: Array of required plugins
- `config`: Object with default values (NO empty objects)

### Plugin Class (plugin.py)

**CORRECT PATTERN:**
```python
from nonix_di.decorator import injectables
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from nonix_di.resolve import NxInject

# Import services and routers
from .services.my_service import MyService
from .routers.my_router import MyRouter

@web_routers([
    MyRouter
])
@injectables([
    MyService
])
class NxWebMyPlugin(BasePlugin):
    # Inject services if needed in plugin methods
    my_service: MyService = NxInject(MyService)

    # Use _startup for initialization (NOT _configure)
    async def _startup(self, config: Dict[str, Any]):
        # Pass config to services here
        await self.my_service.initialize(config)
```

**CRITICAL RULES:**
- ✅ Use `@injectables` decorator for services
- ✅ Use `@web_routers` decorator for routers
- ❌ NEVER DI register the plugin itself
- ❌ NEVER use `config.get()` with inline defaults
- ❌ NEVER override `_configure()` method
- ✅ Use `_startup()` for initialization logic

### Service Layer

**Base Service Pattern:**
```python
from nonix_web_db.crud import BaseCrudService, CRUDConfig

class MyService(BaseCrudService):
    # Only add __init__ if you actually need it
    def __init__(self):
        super().__init__()
        # Only if you have actual initialization logic
        self.config_value = None

    # Add initialize method if plugin passes config
    async def initialize(self, config: Dict[str, Any]):
        self.config_value = config["setting"]

    # CRUDConfig for database operations
    config = CRUDConfig(
        model=MyModel,
        create_schema=MyCreate,
        update_schema=MyUpdate,
        response_schema=MyResponse,
        filters=FilterConfig(...),
        sorting=SortingConfig(...),
        validation=ValidationConfig(...),
        selector=SelectorConfig(...)
    )
```

**Rules:**
- ✅ Inherit from `BaseCrudService` for DB operations
- ✅ Add `__init__` only if you have real initialization
- ✅ Add `initialize()` method if plugin passes config
- ✅ Use `CRUDConfig` for database operations

### Router Layer

**Router Pattern:**
```python
from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject

from ..services.my_service import MyService

@router("/my-endpoints", tags=["My Endpoints"])
class MyRouter(NxWebServerCrudRouter):
    service: MyService = NxInject(MyService)

    @route('/custom', methods=['POST'])
    async def custom_endpoint(self, data: MySchema):
        # Use self.service for business logic
        return await self.service.custom_method(data)
```

**Rules:**
- ✅ Inherit from `NxWebServerCrudRouter`
- ✅ Use `@router` decorator with path and tags
- ✅ Use `@route` decorator for custom endpoints
- ✅ Inject services with `NxInject`

## Configuration System

### Plugin Configuration Flow

1. **Default Config**: Defined in `plugin.json`
2. **Override Config**: Can be overridden in `main.py`
3. **Plugin Receives**: Merged config in `_startup()` method
4. **Services Receive**: Config passed via `initialize()` method

### Main.py Plugin Configuration

```python
settings.PLUGINS = [
    {"name": "my-plugin"},
    {
        "name": "my-plugin-with-config",
        "config": {
            "custom_setting": "custom_value"
        }
    }
]
```

### Service Configuration

```python
class MyService(BaseCrudService):
    async def initialize(self, config: Dict[str, Any]):
        # Direct assignment from config
        self.setting = config["setting_name"]
```

## Frontend Plugin Architecture

### Vue Component Structure

```
vue_libs/nonix-[plugin_name]/
├── services/            # API service classes
├── components/          # Vue components
├── index.js            # Plugin exports
└── [other files]
```

### Service Pattern

```javascript
import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class MyService extends NxCrudService {
    constructor(app) {
        super(app, 'my-endpoints', {
            table: {
                columns: [...]
            },
            form: {
                fields: [...]
            }
        })
    }

    customMethod(data) {
        return this.post('/custom', data)
    }
}
```

### Component Patterns

```vue
<template>
  <div>
    <!-- Component template -->
  </div>
</template>

<script>
import MyService from '../services/MyService.js'

export default {
  name: 'MyComponent',
  inject: ['myService'],
  data() {
    return {
      // Component data
    }
  },
  methods: {
    async loadData() {
      // Use injected service
      const result = await this.myService.getAll()
      this.data = result.data
    }
  }
}
</script>
```

## Dependency Injection System

### Backend DI

**Service Registration:**
```python
@injectables([
    MyService,
    AnotherService
])
class MyPlugin(BasePlugin):
    pass
```

**Service Injection:**
```python
class MyRouter(NxWebServerCrudRouter):
    service: MyService = NxInject(MyService)
```

### Frontend DI

**Service Registration:**
```javascript
// In main app or plugin bootstrap
app.provide('myService', new MyService(app))
```

**Service Injection:**
```javascript
export default {
  inject: ['myService'],
  methods: {
    useService() {
      return this.myService.getData()
    }
  }
}
```

## Database Integration

### Model Definition

```python
from sqlalchemy import Column, Integer, String
from nonix_web_db import BaseModel

class MyModel(BaseModel):
    __tablename__ = 'my_models'

    name = Column(String(255), nullable=False)
    # Other fields...
```

### CRUD Operations

```python
class MyService(BaseCrudService):
    config = CRUDConfig(
        model=MyModel,
        create_schema=MyCreateSchema,
        update_schema=MyUpdateSchema,
        response_schema=MyResponseSchema,
        filters=FilterConfig(
            allowed_fields=['name', 'status']
        ),
        sorting=SortingConfig(
            default_sort='created_at',
            allowed_fields=['created_at', 'name']
        )
    )
```

## Router Registration

### Automatic Registration

```python
@web_routers([
    MyRouter,
    AnotherRouter
])
class MyPlugin(BasePlugin):
    pass
```

### Manual Registration

```python
class MyPlugin(BasePlugin):
    def _startup(self, config: Dict[str, Any]):
        # Manual router registration if needed
        pass
```

## Error Handling

### Backend Error Handling

```python
from fastapi import HTTPException

class MyService(BaseCrudService):
    async def my_method(self, data):
        try:
            # Business logic
            result = await self.process_data(data)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

### Frontend Error Handling

```javascript
export default class MyService extends NxCrudService {
    async myMethod(data) {
        try {
            const response = await this.post('/my-endpoint', data)
            return response
        } catch (error) {
            if (error.status === 400) {
                throw new Error('Invalid data provided')
            }
            throw new Error('Service unavailable')
        }
    }
}
```


## Common Mistakes to Avoid

### ❌ WRONG PATTERNS

1. **Dum AI comments:**
Do mot all dum comments as a comment maximum extends the  Readable CODE!
so manly there is never any code needed!! 
never use DUMB comments  like, tell what is changed or such  as that is CRAP AI comments!!!

2. **Inline Config Defaults:**
```python
# WRONG
self.setting = config.get('setting', 'default')
```

3. **Plugin DI Registration:**
```python
# WRONG
di_register(MyPlugin, instance=self)
```

4. **Empty Constructors:**
```python
# WRONG
def __init__(self):
    super().__init__()
```

5. **Wrong Import Order:**
```python
# WRONG - models after services
from .services.my_service import MyService
from .models.my_model import MyModel
```


5. **Inline Imports**
Do never use inline imports! 
Inline imports are illegal and no allowed


### ✅ CORRECT PATTERNS

1. **Proper Config:**
```json
"config": {
  "setting": "value"
}
```

2. **Direct Config Assignment:**
```python
self.setting = config["setting"]
```

3. **No Plugin Registration:**
```python
# Plugin registers services via decorators only
```

4. **Meaningful Constructors:**
```python
def __init__(self):
    super().__init__()
    self.important_attr = None  # Only if needed
```

5. **Correct Import Order:**
```python
# Models first, then services
from .models.my_model import MyModel
from .services.my_service import MyService
```


6. **Correct Import Order:**
```python
# Models first, then services
from .models.my_model import MyModel
from .services.my_service import MyService
```
## Plugin Development Workflow

1. **Plan Structure**: Define models, services, routers needed
2. **Create Models**: Define database models first
3. **Create Schemas**: Define Pydantic schemas for API
4. **Create Services**: Implement business logic
5. **Create Routers**: Define API endpoints
6. **Configure Plugin**: Set up plugin.json and plugin.py
7. **Register Plugin**: Add to main.py PLUGINS list
8. **Test Integration**: Verify plugin loads and works

## File Organization Standards

### Backend Files
- `plugin.json`: Plugin metadata
- `plugin.py`: Main plugin class
- `models/__init__.py`: Model exports
- `models/my_model.py`: Individual model files
- `services/__init__.py`: Service exports
- `services/my_service.py`: Individual service files
- `routers/__init__.py`: Router exports
- `routers/my_router.py`: Individual router files

### Frontend Files
- `index.js`: Plugin exports and registration
- `services/MyService.js`: API service classes
- `components/MyComponent.vue`: Vue components
- `utils/helpers.js`: Utility functions

## Version Control Guidelines

### Commit Messages
```
feat: add file upload functionality
fix: resolve plugin configuration issue
refactor: simplify service initialization
docs: update plugin development guide
```

### Branch Naming
```
feature/add-file-manager-plugin
fix/file-upload-validation
refactor/plugin-architecture
```

## Performance Considerations

### Database Optimization
- Use appropriate indexes
- Implement pagination for large datasets
- Use async operations for I/O

### Frontend Optimization
- Lazy load components
- Implement virtual scrolling for large lists
- Use computed properties for expensive operations

### Caching Strategies
- Cache frequently accessed data
- Implement appropriate cache invalidation
- Use Redis for distributed caching if needed

## Security Best Practices

### Input Validation
```python
# Backend
from pydantic import BaseModel, Field

class MySchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
```

### Authentication
```python
# Check user permissions
async def create_item(self, data: MySchema, user: User = Depends(get_current_user)):
    # Authorization logic
    pass
```

### Data Sanitization
```javascript
// Frontend
const cleanData = {
    name: sanitizeInput(userInput.name),
    email: validateEmail(userInput.email)
}
```

This comprehensive guide ensures consistent plugin development across the entire Nonix ecosystem. Follow these patterns exactly to avoid architectural issues and maintain code quality.
