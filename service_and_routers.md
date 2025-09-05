# Service & Router Architecture Guide

## 🎯 OVERVIEW

This guide documents the **DRY (Don't Repeat Yourself)** architecture for converting legacy CRUD routers to a clean service/router separation pattern.

### Architecture Goals:
- ✅ **DRY Principle**: No CRUD config duplication across routers
- ✅ **Clean Separation**: Services handle business logic, routers handle HTTP
- ✅ **DI Integration**: Services registered in dependency injection system
- ✅ **Reusable Services**: Services can be injected by other plugins
- ✅ **API Compatibility**: All existing HTTP endpoints preserved

---

## 📋 WHAT TO CHANGE

### 1. 🚫 REMOVE from Router: CRUD Config
```python
# ❌ OLD - CRUD config in router (REPEAT THIS FOR EVERY ROUTER)
class SomeRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=SomeModel,
        create_schema=SomeCreate,
        update_schema=SomeUpdate,
        response_schema=SomeInDbModel,
        filters=FilterConfig(...),
        sorting=SortingConfig(...),
        validation=ValidationConfig(...),
        selector=SelectorConfig(...)
    )

# ✅ NEW - No config in router
class SomeRouter(NxWebServerCrudRouter):
    service: SomeService = Inject(SomeService)
```

### 2. 🚫 REMOVE from Router: Complex Business Logic
```python
# ❌ OLD - Business logic mixed with HTTP
class SomeRouter(NxWebServerCrudRouter):
    async def complex_business_method(self, data):
        # Business logic in router = BAD
        pass

# ✅ NEW - Business logic in service, router delegates
class SomeRouter(NxWebServerCrudRouter):
    service: SomeService = Inject(SomeService)

    async def complex_business_method(self, data):
        return await self.service.complex_business_method(data)  # Delegate
```

### 3. 🔄 MOVE from Router to Service: CRUD Configuration
```python
# ❌ OLD - Config in router
# ✅ NEW - Config moved to service

class SomeService(BaseCrudService):
    config = CRUDConfig(  # ← MOVED HERE
        model=SomeModel,
        create_schema=SomeCreate,
        update_schema=SomeUpdate,
        response_schema=SomeInDbModel,
        filters=FilterConfig(...),
        sorting=SortingConfig(...),
        validation=ValidationConfig(...),
        selector=SelectorConfig(...)
    )
```

### 4. 🔄 CONVERT from Router Method to Service Method
```python
# ❌ OLD - Router method with session management
async def some_method(self, data):
    async with AsyncSessionLocal() as session:
        # Complex business logic here
        pass

# ✅ NEW - Service method with internal session management
async def some_method(self, data):
    async with AsyncSessionLocal() as session:
        # Same logic, but in service
        pass
```

---

## 📋 WHAT TO *NOT* CHANGE

### 1. ✅ PRESERVE: HTTP Endpoints & Routes
```python
# ✅ KEEP - All existing API endpoints unchanged
GET  /some-entities
POST /some-entities
GET  /some-entities/{id}
PUT  /some-entities/{id}
DELETE /some-entities/{id}
```

### 2. ✅ PRESERVE: Query Parameters & Features
```python
# ✅ KEEP - All query parameter functionality
GET /some-entities?page=1&per_page=20&order_by=name&filter_name=John
GET /some-entities/search?q=search_term
```

### 3. ✅ PRESERVE: HTTP Status Codes
```python
# ✅ KEEP - Same status codes
POST /some-entities → 201 Created
DELETE /some-entities/{id} → 204 No Content
```

### 4. ✅ PRESERVE: Response Models & Serialization
```python
# ✅ KEEP - Same response schemas
@router.post("/", response_model=SomeInDbModel)
async def create(data: SomeCreate):
    # Response model unchanged
```

### 5. ✅ PRESERVE: Custom HTTP Routes
```python
# ✅ KEEP - Custom routes with their HTTP decorators
@route("/custom-endpoint", methods=["POST"])
async def custom_endpoint(self, data):
    # Custom HTTP logic preserved
```

### 6. ✅ PRESERVE: HTTP Error Handling
```python
# ✅ KEEP - HTTP exceptions and status codes
raise HTTPException(status_code=404, detail="Not found")
raise HTTPException(status_code=409, detail="Conflict")
```

### 7. ✅ PRESERVE: Authentication & Middleware
```python
# ✅ KEEP - All auth decorators and middleware
@router.get("/protected", dependencies=[Depends(get_current_user)])
async def protected_route(self):
    # Auth logic unchanged
```

---

## 🔄 STEP-BY-STEP CONVERSION PROCESS

### Phase 1: Create Service
```bash
# 1. Create services directory
mkdir -p plugin/services

# 2. Create service file
touch plugin/services/some_service.py

# 3. Create __init__.py
touch plugin/services/__init__.py
```

### Phase 2: Move CRUD Config
```python
# 1. Copy config from router
# 2. Paste into service
# 3. Remove from router

class SomeService(BaseCrudService):
    config = CRUDConfig(...)  # ← MOVED FROM ROUTER
```

### Phase 3: Convert Router
```python
# 1. Remove config from router
# 2. Add service injection
# 3. Preserve custom routes

class SomeRouter(NxWebServerCrudRouter):
    service: SomeService = Inject(SomeService)  # ← NEW

    @route("/custom", methods=["GET"])  # ← PRESERVE
    async def custom_method(self):
        return await self.service.custom_method()  # ← DELEGATE
```

### Phase 4: Register Service
```python
# 1. Import service in plugin
from .services.some_service import SomeService

# 2. Register in DI
class SomePlugin(BasePlugin):
    def _configure(self, server, config):
        di_register(SomeService)  # ← REGISTER
```

---

## 📁 FILE STRUCTURE CHANGES

### Before (Mixed):
```
plugin/
├── routers/
│   └── some_router.py     # ❌ CRUD config + HTTP logic
└── models/
    └── some_model.py      # ✅ Unchanged
```

### After (Separated):
```
plugin/
├── services/
│   ├── __init__.py        # ✅ NEW
│   └── some_service.py    # ✅ NEW - CRUD config + business logic
├── routers/
│   └── some_router.py     # ✅ MODIFIED - Service injection + HTTP logic
└── models/
    └── some_model.py      # ✅ Unchanged
```

---

## 🔧 DETAILED CONVERSION EXAMPLE

### 1. Original Router (BAD):
```python
class SomeRouter(NxWebServerCrudRouter):
    config = CRUDConfig(  # ❌ DON'T DO THIS
        model=SomeModel,
        create_schema=SomeCreate,
        update_schema=SomeUpdate,
        response_schema=SomeInDbModel,
        # ... lots of duplicated config
    )

    async def custom_method(self, data):
        async with AsyncSessionLocal() as session:
            # Business logic in router = BAD
            pass
```

### 2. New Service (GOOD):
```python
class SomeService(BaseCrudService):
    config = CRUDConfig(  # ✅ DO THIS INSTEAD
        model=SomeModel,
        create_schema=SomeCreate,
        update_schema=SomeUpdate,
        response_schema=SomeInDbModel,
        # ... same config, but centralized
    )

    async def custom_method(self, data):
        async with AsyncSessionLocal() as session:
            # Same business logic, but in service = GOOD
            pass
```

### 3. New Router (GOOD):
```python
class SomeRouter(NxWebServerCrudRouter):
    service: SomeService = Inject(SomeService)  # ✅ DO THIS

    async def custom_method(self, data):
        return await self.service.custom_method(data)  # ✅ DELEGATE
```

---

## 🚨 CRITICAL RULES

### ✅ DO Change:
- Move CRUD config from router to service
- Add service injection to router
- Convert router business logic to service methods
- Register services in DI system
- Create services directory structure

### ❌ DON'T Change:
- HTTP endpoint paths
- Query parameter names/features
- Response models/schemas
- HTTP status codes
- Custom route decorators
- Authentication/authorization
- Middleware usage
- Error response formats

### 🔄 MAY Change (Optional):
- Internal method names (if not exposed via HTTP)
- Code organization within services
- Additional service methods (but don't add new API endpoints)

---

## 🧪 TESTING CHECKLIST

After conversion, verify:
- ✅ All existing endpoints return same responses
- ✅ All query parameters work identically
- ✅ HTTP status codes unchanged
- ✅ Authentication still works
- ✅ Custom routes preserved
- ✅ No new API features added (unless explicitly requested)

---

## 🎯 SUMMARY

**CHANGE**: Business logic, CRUD config, service architecture
**PRESERVE**: HTTP interface, API contract, user experience

This ensures **architectural improvement** without **breaking changes**! 🎯
