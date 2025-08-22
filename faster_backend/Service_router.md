# ServiceRouter Requirements

## ServiceRouter should be EXACTLY like APIRouter:

### What to REMOVE (unwanted auto-created routes):
- **NO `/api/services`** - remove utility endpoint
- **NO `/api/services/info`** - remove utility endpoint  
- **NO `/api/services/{service_name}`** - remove utility endpoint
- **NO `/api/health`** - remove health check
- **NO `/api/overview`** - remove overview
- **NO `/api/ws/service/{service_name}`** - remove service-specific WebSocket routes

### What to KEEP (like APIRouter):
- **ONLY registered service endpoints**:
  - `/api/artists`
  - `/api/albums`
  - `/api/tracks`
  - etc.

### What to ADD (only difference from APIRouter):
- **ONLY ONE WebSocket endpoint**:
  - `/api/ws` - single WebSocket access point for connections

### WebSocket behavior:
- **NO channels, NO namespaces, NO other crap**
- **WebSocket rooms happen via WebSocket registration** - join/leave via WebSocket messages, not URL routes
- **Single connection point at `/api/ws`**

## Summary:
**ServiceRouter = APIRouter + `/api/ws`**

- Clean, simple, only HTTP routes for registered services
- NO utility endpoints, NO magic routes
- ONE WebSocket endpoint at `/api/ws`
- EXACTLY like APIRouter with only the WebSocket addition
