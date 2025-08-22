# Service Router FastAPI Migration Guide

## Overview
This document outlines the step-by-step process to convert the Flask-based `service_router` to work with FastAPI, making all services accessible at `/api/*` endpoints.

## Current State Analysis
- **service_router**: Currently uses Flask Blueprint and Flask-specific routing
- **api_router**: Already converted to FastAPI and working
- **Goal**: Make service_router work with FastAPI so all services are accessible at `/api/*`

---

## PHASE 1: Core Router Replacement
### 1.1 Replace Flask Blueprint with FastAPI APIRouter
**File**: `faster_backend/app/api/service_router/service_router.py`

**Current Code**:
```python
from flask import Blueprint, request, current_app
# ...
self.blueprint: Blueprint = Blueprint('api', __name__)
```

**Change To**:
```python
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
# ...
self.router: APIRouter = APIRouter(prefix="/api")
```

### 1.2 Update Route Registration Method
**Current**: Uses `add_url_rule()` with Flask Blueprint
**New**: Use FastAPI route decorators and dynamic route creation

**Replace This**:
```python
self.blueprint.add_url_rule(
    await self._normalize_path(service_name, getattr(method, '_path')),
    endpoint=f"{service_name}:{getattr(method, '__name__', 'endpoint')}:{await self._normalize_path(service_name, getattr(method, '_path'))}",
    view_func=await handler_factory(method),
    methods=getattr(method, '_methods', ['GET'])
)
```

**With This**:
```python
# Create FastAPI route dynamically
path = await self._normalize_path(service_name, getattr(method, '_path'))
methods = getattr(method, '_methods', ['GET'])

for method_name in methods:
    if method_name.upper() == 'GET':
        self.router.get(path)(await handler_factory(method))
    elif method_name.upper() == 'POST':
        self.router.post(path)(await handler_factory(method))
    elif method_name.upper() == 'PUT':
        self.router.put(path)(await handler_factory(method))
    elif method_name.upper() == 'DELETE':
        self.router.delete(path)(await handler_factory(method))
    elif method_name.upper() == 'PATCH':
        self.router.patch(path)(await handler_factory(method))
```

---

## PHASE 2: Request Handling Updates
### 2.1 Replace Flask Request with FastAPI Request
**Current Code**:
```python
from flask import request, current_app
# ...
result = await bound_method(request, **kwargs)
```

**Change To**:
```python
from fastapi import Request
# ...
result = await bound_method(request, **kwargs)
```

### 2.2 Update Error Handling
**Current**: Uses Flask `current_app.config.get('DEBUG')`
**New**: Use FastAPI's built-in error handling

**Replace This**:
```python
return JSONResponse({
    'error': 'Service Error',
    'service': service_name,
    'method': bound_method.__name__,
    'message': str(e),
    'traceback': traceback.format_exc() if current_app.config.get('DEBUG') else None
}, 500)
```

**With This**:
```python
return JSONResponse(
    {
        'error': 'Service Error',
        'service': service_name,
        'method': bound_method.__name__,
        'message': str(e),
        'traceback': traceback.format_exc() if settings.DEBUG else None
    },
    500
)
```

---

## PHASE 3: Path Parameter Handling
### 3.1 Update Path Normalization
**Current**: Converts `{id}` to Flask `<id>` syntax
**New**: Keep `{id}` syntax (FastAPI native)

**Replace This**:
```python
async def _normalize_path(self, service_name: str, path: str) -> str:
    if not path.startswith('/'):
        path = '/' + path
    # Convert `{id}` style placeholders to Flask `<id>`
    flask_path = path.replace('{', '<').replace('}', '>')
    return f'/{service_name}{path}'
```

**With This**:
```python
async def _normalize_path(self, service_name: str, path: str) -> str:
    if not path.startswith('/'):
        path = '/' + path
    # Keep {id} syntax for FastAPI
    return f'/{service_name}{path}'
```

---

## PHASE 4: Documentation Router Updates
### 4.1 Replace Flask Routes with FastAPI Endpoints
**File**: `faster_backend/app/api/service_router/documentation_router.py`

**Current Code**:
```python
from flask import jsonify, request
# ...
@self.blueprint.route('/openapi.json')
async def openapi_spec():
    # ... Flask code ...
    return jsonify(result)
```

**Change To**:
```python
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
# ...
@self.router.get('/openapi.json')
async def openapi_spec(request: Request):
    # ... FastAPI code ...
    return JSONResponse(content=result)
```

### 4.2 Update Request Handling
**Current**: Uses Flask `request.args.get('services')`
**New**: Use FastAPI query parameters

**Replace This**:
```python
service_filter = request.args.get('services', None)
```

**With This**:
```python
from fastapi import Query
# ...
async def openapi_spec(services: str = Query(None, alias='services')):
    service_filter = services
```

---

## PHASE 5: Base Service Updates
### 5.1 Update Path Parameter Extraction
**File**: `faster_backend/app/api/service_router/base_service.py`

**Current**: Extracts `{param_name}` patterns
**New**: Keep same logic (FastAPI compatible)

**No Changes Needed**: The current `{param_name}` extraction is already FastAPI compatible.

### 5.2 Update Swagger Generation
**Current**: Generates OpenAPI schemas
**New**: Ensure compatibility with FastAPI's OpenAPI format

**No Major Changes Needed**: The current OpenAPI generation should work with FastAPI.

---

## PHASE 6: Integration with FastAPI App
### 6.1 Update Main App File
**File**: `faster_backend/app/__init__.py`

**Add This After Line 45**:
```python
from .api.service_router.service_router import ServiceRouter

# Initialize service router
service_router_instance = ServiceRouter()
app.include_router(service_router_instance.router, tags=["services"])
```

### 6.2 Update API Init File
**File**: `faster_backend/app/api/__init__.py`

**Add This**:
```python
from .service_router.service_router import ServiceRouter

# Create service router instance
service_router = ServiceRouter()

__all__ = ["api_router", "service_router"]
```

---

## PHASE 7: WebSocket Integration
### 7.1 Update WebSocket Handling
**Current**: Uses SocketIO
**New**: Integrate with FastAPI's WebSocket support

**Update ServiceRouter Constructor**:
```python
def __init__(self) -> None:
    self.router: APIRouter = APIRouter(prefix="/api")
    self.registered_services: dict[str, BaseService] = {}
    self.logger: logging.Logger = logging.getLogger(__name__)
    # Remove SocketIO dependency for now
    # self.socketio: Any = socketio_instance
    self._websocket_channels: dict[str, dict] = {}
```

---

## PHASE 8: Testing and Validation
### 8.1 Test Route Registration
1. Start the FastAPI server
2. Check `/docs` endpoint for automatic OpenAPI documentation
3. Verify all service routes appear under `/api/*`
4. Test individual endpoints

### 8.2 Validate OpenAPI Generation
1. Check `/openapi.json` endpoint
2. Verify all service paths are included
3. Check that path parameters use `{id}` syntax
4. Validate request/response schemas

---

## PHASE 9: Cleanup and Optimization
### 9.1 Remove Flask Dependencies
- Remove all `flask` imports
- Remove `Blueprint` references
- Clean up unused Flask-specific code

### 9.2 Optimize FastAPI Features
- Add Pydantic models for request/response validation
- Use FastAPI's dependency injection where appropriate
- Leverage FastAPI's automatic response serialization

---

## Expected Results After Migration
- ✅ All services accessible at `/api/*` endpoints
- ✅ Automatic OpenAPI documentation at `/docs`
- ✅ FastAPI-native path parameter handling (`{id}`)
- ✅ Better performance and type safety
- ✅ Unified framework (both frontend and backend use FastAPI)
- ✅ Modern async/await support
- ✅ Built-in request/response validation

---

## Files to Modify (In Order)
1. `faster_backend/app/api/service_router/service_router.py` (PHASE 1-3)
2. `faster_backend/app/api/service_router/documentation_router.py` (PHASE 4)
3. `faster_backend/app/api/service_router/base_service.py` (PHASE 5)
4. `faster_backend/app/__init__.py` (PHASE 6)
5. `faster_backend/app/api/__init__.py` (PHASE 6)

## Dependencies to Add
```python
# In requirements.txt or install manually
fastapi>=0.100.0
uvicorn>=0.20.0
```

## Testing Commands
```bash
# Start the FastAPI server
cd faster_backend
uvicorn app.main:app --reload

# Check endpoints
curl http://localhost:8000/api/
curl http://localhost:8000/docs
curl http://localhost:8000/openapi.json
```

---

## Troubleshooting Common Issues

### Issue 1: Routes Not Appearing
- Check that `service_router.router` is included in the main app
- Verify service registration is working
- Check FastAPI logs for errors

### Issue 2: Path Parameters Not Working
- Ensure paths use `{id}` syntax, not `<id>`
- Check that path normalization preserves `{id}` format
- Verify FastAPI route decorators are correct

### Issue 3: OpenAPI Documentation Missing
- Check that all services have proper `@expose` decorators
- Verify `to_swagger()` method returns valid OpenAPI format
- Check that service tags are properly set

### Issue 4: WebSocket Issues
- Temporarily disable WebSocket features during migration
- Focus on HTTP endpoints first
- Add WebSocket support back after HTTP routes work

---

## Migration Checklist
- [ ] PHASE 1: Replace Flask Blueprint with FastAPI APIRouter
- [ ] PHASE 2: Update request handling
- [ ] PHASE 3: Fix path parameter handling
- [ ] PHASE 4: Update documentation router
- [ ] PHASE 5: Verify base service compatibility
- [ ] PHASE 6: Integrate with main FastAPI app
- [ ] PHASE 7: Handle WebSocket integration
- [ ] PHASE 8: Test all endpoints
- [ ] PHASE 9: Clean up and optimize

---

## Notes
- Follow phases in order - each builds on the previous
- Test after each phase to catch issues early
- Keep Flask version as backup until migration is complete
- Focus on HTTP endpoints first, WebSocket second
- Use FastAPI's built-in features instead of custom implementations
