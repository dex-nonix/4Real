# ServiceRouter Requirements

## FINDINGS - What was discovered:

### ServiceRouter (faster_backend) currently has:
- DocumentationRouter with `/api/openapi.json` and `/api/docs` routes
- CompactApiGenerator and OpenAPIGenerator
- ~~WebSocket discovery and storage (WRONG - should be removed)~~ ✅ **REMOVED**
- ~~WebSocket routes at `/api/ws/service/{channel}` (WRONG - should be only `/api/ws`)~~ ✅ **REMOVED**
- Service registration for HTTP endpoints
- ~~PLUS unwanted utility endpoints: `/api/services/*`, `/api/health`, `/api/overview`~~ ✅ **REMOVED**

### EXISTING WebSocket System (KEEP THIS):
- `faster_backend/app/websocket/manager.py` - `ConnectionManager` class (ALREADY PERFECT!)
- `faster_backend/app/websocket/handlers.py` - WebSocket message handling (ALREADY PERFECT!)
- Single `/api/ws` endpoint with room-based messaging (ALREADY IMPLEMENTED!)

## WHAT NEEDS TO BE DONE:

### ✅ REMOVE these unwanted routes from ServiceRouter:
- ~~`/api/services` - utility endpoint~~ ✅ **REMOVED**
- ~~`/api/services/info` - utility endpoint~~ ✅ **REMOVED**  
- ~~`/api/services/{service_name}` - utility endpoint~~ ✅ **REMOVED**
- ~~`/api/health` - health check~~ ✅ **REMOVED**
- ~~`/api/overview` - compact YAML overview~~ ✅ **REMOVED**
- ~~`/api/ws/service/{channel}` - service-specific WebSocket route (WRONG!)~~ ✅ **REMOVED**

### ✅ REMOVE these unwanted WebSocket components from ServiceRouter:
- ~~`_websocket_channels` dictionary~~ ✅ **REMOVED**
- ~~`_discover_websocket_channels()` method~~ ✅ **REMOVED**
- ~~`_handle_websocket_connection()` with channel parameter~~ ✅ **REMOVED**
- ~~`_handle_service_websocket_connection()` method~~ ✅ **REMOVED**
- ~~`broadcast_to_channel()` method~~ ✅ **REMOVED**
- ~~All `@expose_ws` discovery logic~~ ✅ **REMOVED**
- ~~`_add_websocket_endpoints()` method~~ ✅ **REMOVED**

### ✅ USE EXISTING WebSocket System:
- **KEEP existing**: `/api/ws` endpoint (already working!)
- **KEEP existing**: `ConnectionManager` class (already room-based!)
- **KEEP existing**: Room-based messaging system (already implemented!)
- **ADD**: Service integration method to existing `ConnectionManager` ✅ **COMPLETED**

### ✅ KEEP these routes:
- `/api/artists`, `/api/albums`, `/api/tracks` - registered service endpoints
- `/api/openapi.json`, `/api/docs` - documentation routes
- `/api/ws` - WebSocket endpoint (SINGLE endpoint only!)

### ✅ KEEP these components:
- DocumentationRouter
- CompactApiGenerator
- OpenAPIGenerator
- Service registration system for HTTP endpoints
- BaseService integration
- **EXISTING WebSocket system** (`faster_backend/app/websocket/`)

## FINAL RESULT - What ServiceRouter should be:

### ✅ WebSocket System (USE EXISTING):
- **Single connection point**: `/api/ws` only (ALREADY EXISTS!)
- **No channels**: Never any `/api/ws/{channel}` routes ✅ **ACHIEVED**
- **No namespaces**: Simple room-based system (ALREADY IMPLEMENTED!)
- **Room management**: Clients send "join" and "leave" messages with room names (ALREADY WORKING!)
- **Message broadcasting**: Services use existing `ConnectionManager` to send to rooms ✅ **IMPLEMENTED**
- **Client subscription**: Clients can listen to 0-n rooms simultaneously (ALREADY WORKING!)

### ✅ HTTP API System:
- Service registration with `@expose` decorator (unchanged)
- Routes like `/api/{servicename}/{exposed_method}` (unchanged)
- All existing service functionality preserved

### ✅ Documentation System:
- Use custom swagger generator (not FastAPI docs)
- Keep existing DocumentationRouter, CompactApiGenerator, OpenAPIGenerator
- Maintain `/api/openapi.json` and `/api/docs` routes

### ✅ NO MORE:
- ~~`@expose_ws` decorator or discovery~~ ✅ **REMOVED**
- ~~Channel-based WebSocket architecture~~ ✅ **REMOVED**
- ~~Multiple WebSocket endpoints~~ ✅ **REMOVED**
- ~~Utility endpoints~~ ✅ **REMOVED**
- FastAPI built-in documentation
- ~~**DUPLICATE WebSocket code in ServiceRouter**~~ ✅ **REMOVED**

## IMPLEMENTATION APPROACH:

### ✅ 1. **Remove WebSocket code from ServiceRouter** (clean slate) ✅ **COMPLETED**
- Delete all channel-based WebSocket methods and data structures ✅ **DONE**
- Remove utility endpoints ✅ **DONE**
- Keep only HTTP API routing functionality ✅ **DONE**

### ✅ 2. **Use existing ConnectionManager** (no new classes needed!) ✅ **COMPLETED**
- The existing `faster_backend/app/websocket/manager.py` is already perfect ✅ **CONFIRMED**
- It already has room-based messaging, no channels, no namespaces ✅ **CONFIRMED**
- Just add one method for service integration if needed ✅ **IMPLEMENTED**

### ✅ 3. **Update BaseService integration** ✅ **COMPLETED**
- Remove `send_to_channel()` method ✅ **DONE**
- Add method to use existing `ConnectionManager` for room messaging ✅ **DONE**
- Keep service router reference for other purposes ✅ **DONE**

### ✅ 4. **Ensure single endpoint** ✅ **COMPLETED**
- Verify `/api/ws` uses existing WebSocket system ✅ **CONFIRMED**
- Remove any duplicate WebSocket routes from ServiceRouter ✅ **DONE**

## SUCCESS CRITERIA:
- [x] ServiceRouter only handles HTTP API routing (clean separation) ✅ **ACHIEVED**
- [x] WebSocket functionality handled by existing `ConnectionManager` ✅ **ACHIEVED**
- [x] Single `/api/ws` endpoint with room-based messaging ✅ **ACHIEVED**
- [x] No channel-based architecture anywhere ✅ **ACHIEVED**
- [x] Services can send messages to rooms via existing system ✅ **ACHIEVED**
- [x] HTTP API system unchanged ✅ **ACHIEVED**
- [x] Documentation system unchanged ✅ **ACHIEVED**
- [x] No utility endpoints exist ✅ **ACHIEVED**
- [x] Clean, maintainable code structure ✅ **ACHIEVED**
- [x] **NO NEW CLASSES CREATED** - reuse existing perfect system! ✅ **ACHIEVED**

## 🎉 IMPLEMENTATION STATUS: COMPLETE! ✅

**All phases have been successfully implemented:**
- ✅ **Phase 1**: Remove all WebSocket code from ServiceRouter
- ✅ **Phase 2**: Remove utility endpoints  
- ✅ **Phase 3**: Update BaseService integration
- ✅ **Phase 4**: Remove @expose_ws decorator

**ServiceRouter is now clean, focused, and uses the existing perfect WebSocket system!**
