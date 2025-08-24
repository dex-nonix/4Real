# Service Conversion Guide: Old Framework → New Framework

## Overview
This document provides step-by-step instructions for converting services from the old `CrudService` framework to the new `GenericCRUDService` framework with Pydantic schemas.

## Framework Differences

### Old Framework (`faster_backend/app/api/services/`)
- **Base Class**: `CrudService` (558 lines, complex)
- **Configuration**: Simple dictionary configs
- **Schema Management**: Manual handling
- **Route Registration**: Manual decorators
- **Location**: `faster_backend/app/api/services/{service_name}.py`

### New Framework (`faster_backend/app/services/`)
- **Base Class**: `GenericCRUDService` (clean, structured)
- **Configuration**: `CRUDConfig` with Pydantic models
- **Schema Management**: Structured Pydantic schemas
- **Route Registration**: Automatic via `GenericCRUDService`
- **Location**: `faster_backend/app/services/{service_name}/`

## Conversion Structure

### Required Files Per Service
Each service needs **2 files** in a dedicated folder:

```
faster_backend/app/services/{service_name}/
├── __init__.py                    # Package initialization
├── {service_name}_schemas.py      # Pydantic models
└── {service_name}_service.py      # Service class
```

### File Templates

#### 1. `{service_name}_schemas.py`
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from ..base_schemas import BaseDBMixin

class {ServiceName}Base(BaseModel):
    # Define base fields (without id, created_at, updated_at)
    field1: str = Field(..., min_length=1, max_length=255)
    field2: Optional[str] = Field(None, max_length=50)
    field3: Optional[date] = None

class {ServiceName}Create({ServiceName}Base):
    pass

class {ServiceName}Update({ServiceName}Base):
    pass

class {ServiceName}InDB({ServiceName}Base, BaseDBMixin):
    pass
```

#### 2. `{service_name}_service.py`
```python
from .{service_name}_schemas import {ServiceName}Create, {ServiceName}Update, {ServiceName}InDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import {ServiceName}

@routed_service("/{service_name}s", tags=["{ServiceName}s"])
class {ServiceName}Service(GenericCRUDService):
    config = CRUDConfig(
        model={ServiceName},
        create_schema={ServiceName}Create,
        update_schema={ServiceName}Update,
        response_schema={ServiceName}InDB,
        filters=FilterConfig(
            allowed_fields=['field1', 'field2']
        ),
        sorting=SortingConfig(
            default_sort='field1',
            allowed_fields=['field1', 'field2', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['field1']
        ),
        selector=SelectorConfig(
            fields=['field1', 'field2'],
            display_format='{field1}',
            search_fields=['field1', 'field2']
        )
    )
```

#### 3. `__init__.py`
```python
from .{service_name}_service import {ServiceName}Service
from .{service_name}_schemas import {ServiceName}Create, {ServiceName}Update, {ServiceName}InDB

__all__ = ['{ServiceName}Service', '{ServiceName}Create', '{ServiceName}Update', '{ServiceName}InDB']
```

## Configuration Mapping

### Old Config → New Config
```python
# OLD (dictionary)
config = {
    'filters': {
        'fields': ['name', 'abbreviation'],
    },
    'sorting': {
        'default_sort': 'name',
        'allowed_fields': ['name', 'abbreviation', 'created_at'],
    },
    'validation': {
        'required_fields': ['name'],        # ❌ Not used in new framework
        'unique_fields': ['name'],
    },
    'selector': {
        'fields': ['name', 'abbreviation'],
        'display_format': 'name',           # ❌ String → Template string
        'search_fields': ['name', 'abbreviation']
    },
}

# NEW (CRUDConfig)
config = CRUDConfig(
    filters=FilterConfig(
        allowed_fields=['name', 'abbreviation']
    ),
    sorting=SortingConfig(
        default_sort='name',
        allowed_fields=['name', 'abbreviation', 'created_at']
    ),
    validation=ValidationConfig(
        unique_fields=['name']              # ✅ Only unique fields needed
    ),
    selector=SelectorConfig(
        fields=['name', 'abbreviation'],
        display_format='{name}',            # ✅ Template string format
        search_fields=['name', 'abbreviation']
    )
)
```

## Services to Convert

### High Priority (Core Services)
1. **ai_analysis_result_service.py** → `ai_analysis_result/`
2. **ai_model_mapping_service.py** → `ai_model_mapping/`
3. **ai_provider_service.py** → `ai_provider/`
4. **chat_history_service.py** → `chat_history/`
5. **chat_message_service.py** → `chat_message/`
6. **chat_session_service.py** → `chat_session/`
7. **file_service.py** → `file/`
8. **persona_service.py** → `persona/`
9. **track_service.py** → `track/`

### Medium Priority
10. **file_category_service.py** → `file_category/`
11. **file_link_service.py** → `file_link/`
12. **internal_tool_service.py** → `internal_tool/`
13. **mcp_server_service.py** → `mcp_server/`
14. **persona_mcp_server_service.py** → `persona_mcp_server/`
15. **persona_tool_access_service.py** → `persona_tool_access/`
16. **rhyme_technique_service.py** → `rhyme_technique/`
17. **style_service.py** → `style/`
18. **tool_invocation_log_service.py** → `tool_invocation_log/`

## Step-by-Step Conversion Process

### Phase 1: Analysis
1. **Examine old service** to understand:
   - Model class being used
   - Current configuration structure
   - Any custom methods or routes
   - Field types and validation rules

2. **Identify model fields** from the database model:
   - Required vs optional fields
   - Field types (str, int, date, datetime, etc.)
   - Validation rules (min_length, max_length, etc.)

### Phase 2: Schema Creation
1. **Create service folder**: `mkdir -p faster_backend/app/services/{service_name}/`
2. **Create schemas file** with proper field definitions
3. **Use BaseDBMixin** for common database fields (id, created_at, updated_at)
4. **Define field validations** using Pydantic Field constraints

### Phase 3: Service Conversion
1. **Create service file** inheriting from `GenericCRUDService`
2. **Convert config dictionary** to `CRUDConfig` structure
3. **Map old config keys** to new Pydantic config objects
4. **Add route decorator** with proper path and tags
5. **Remove old imports** and add new framework imports

### Phase 4: Package Setup
1. **Create `__init__.py`** with proper exports
2. **Test imports** to ensure no circular dependencies
3. **Verify service registration** in the new framework

## Common Conversion Patterns

### Field Type Mappings
```python
# String fields
'name': str = Field(..., min_length=1, max_length=255)

# Optional fields
'abbreviation': Optional[str] = Field(None, max_length=50)

# Date fields
'release_date': Optional[date] = None

# Integer fields with validation
'artist_id': int = Field(..., gt=0)

# Boolean fields
'is_active': bool = True
```

### Display Format Conversion
```python
# OLD
'display_format': 'name'

# NEW
'display_format': '{name}'
```

### Validation Rules
```python
# OLD
'required_fields': ['name', 'artist_id']  # ❌ Not used

# NEW
# Required fields are handled by Pydantic Field(...) syntax
# Only unique_fields are needed in ValidationConfig
```

## Testing Conversion

### Verification Checklist
- [ ] Service folder created with correct structure
- [ ] Schemas file has proper Pydantic models
- [ ] Service file inherits from `GenericCRUDService`
- [ ] Config uses `CRUDConfig` with proper Pydantic objects
- [ ] Route decorator added with correct path and tags
- [ ] `__init__.py` exports all necessary classes
- [ ] No import errors when importing the service
- [ ] Old service file remains unchanged (as requested)

### Common Issues
1. **Import paths**: Ensure relative imports use correct `..` levels
2. **Field validation**: Convert string constraints to Pydantic Field validators
3. **Config structure**: Map old dictionary keys to new Pydantic config objects
4. **Display format**: Convert simple strings to template strings with `{}`

## Example Conversion: Album Service

### Before (Old Framework)
```python
# faster_backend/app/api/services/album_service.py
from .crud_service import CrudService
from ...models.album import Album

class AlbumService(CrudService):
    model = Album
    config = {
        'filters': {'fields': ['title', 'release_date', 'artist_id']},
        'sorting': {'default_sort': 'release_date', 'allowed_fields': ['title', 'release_date', 'created_at']},
        'validation': {'required_fields': ['title', 'artist_id'], 'unique_fields': []},
        'selector': {'fields': ['title', 'release_date'], 'display_format': 'title', 'search_fields': ['title']}
    }
```

### After (New Framework)
```python
# faster_backend/app/services/album/album_schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from ..base_schemas import BaseDBMixin

class AlbumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    release_date: Optional[date] = None
    artist_id: int = Field(..., gt=0)

class AlbumCreate(AlbumBase):
    pass

class AlbumUpdate(AlbumBase):
    pass

class AlbumInDB(AlbumBase, BaseDBMixin):
    pass

# faster_backend/app/services/album/album_service.py
@routed_service("/albums", tags=["Albums"])
class AlbumService(GenericCRUDService):
    config = CRUDConfig(
        model=Album,
        create_schema=AlbumCreate,
        update_schema=AlbumUpdate,
        response_schema=AlbumInDB,
        filters=FilterConfig(allowed_fields=['title', 'release_date', 'artist_id']),
        sorting=SortingConfig(default_sort='release_date', allowed_fields=['title', 'release_date', 'created_at']),
        validation=ValidationConfig(unique_fields=[]),
        selector=SelectorConfig(
            fields=['title', 'release_date'],
            display_format='{title}',
            search_fields=['title']
        )
    )
```

## Notes
- **DO NOT DELETE** original service files - they remain as reference
- **DO NOT START/STOP** dev server during conversion
- **Use BaseDBMixin** for all database schemas to avoid duplication
- **Maintain consistent naming** conventions across all services
