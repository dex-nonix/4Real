# NxWebStt Plugin - Backend Speech-to-Text Conversion

## Overview
Convert the standalone Flask STT application into a proper NxWeb plugin that integrates with the existing framework.

## Source Analysis
**Original Flask App Structure:**
```
nx-sst-server/app/
├── __init__.py          # Flask app initialization
├── routes.py           # HTTP upload endpoint (/upload)
├── websocket.py        # WebSocket real-time processing
├── speech_recognition.py # Core Whisper transcription logic
├── templates/index.html # ❌ IGNORE - Vue.js handles frontend
├── static/styles.css   # ❌ IGNORE - Vue.js handles styling
```

## Target Plugin Architecture (SIMPLE LIKE MCP!)
```
faster_backend/nonix_web_stt/
├── plugin.json                    # Plugin metadata - NO CONFIG!
├── plugin.py                     # Pure plugin setup (NO business logic!)
├── __init__.py
├── models/
│   └── stt_configuration.py     # NxSttConfiguration - ONE table like MCP!
├── schemas/
│   └── stt_configuration_schemas.py # Pydantic schemas like MCP!
├── services/
│   └── stt_service.py           # NxSttService - ONE SERVICE handles everything!
├── routers/
│   └── stt_router.py           # NxSttRouter - ONE router handles everything!
```

## Plugin Metadata (plugin.json)
**NO CONFIG - All STT settings come from DATABASE like MCP!**
```json
{
  "name": "stt",
  "version": "0.1.0",
  "class": "NxWebSttPlugin",
  "dependencies": ["web", "db"],
  "config": {}
}
```

## Core Components

### 1. NxWebSttPlugin (plugin.py)
**NO _startup() needed - like MCP server!**
```python
@injectables([
    NxSttService  # Only ONE service like MCP!
])
@web_routers([
    NxSttRouter
])
class NxWebSttPlugin(BasePlugin):
    # NO _startup() method needed - service loads from database directly!
```

### 2. NxSttService (services/stt_service.py)
**ONE SERVICE HANDLES EVERYTHING - like MCP server!**
```python
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, BaseCrudService

class NxSttService(BaseCrudService):
    # Configuration for CRUD operations (like MCP server)
    config = CRUDConfig(
        model=NxSttConfiguration,
        create_schema=NxSttConfigurationCreate,
        update_schema=NxSttConfigurationUpdate,
        response_schema=NxSttConfigurationInDbModel,
        filters=FilterConfig(allowed_fields=['name', 'is_active']),
        sorting=SortingConfig(default_sort='name', allowed_fields=['name', 'created_at']),
        validation=ValidationConfig(unique_fields=['name']),
        selector=SelectorConfig(fields=['name'], display_format='{name}', search_fields=['name'])
    )

    ws_service: NxWebServerWebSocketService = NxInject(NxWebServerWebSocketService)

    def __init__(self):
        super().__init__()
        self._connections: Dict[str, Dict] = {}  # connection_id -> {buffer, config_id}

    # File-based transcription (from speech_recognition.py)
    async def transcribe_file(self, file_path: str, config_id: int) -> str:
        """File-based transcription using database config - REQUIRES config_id!"""
        config = await self.get_by_id(config_id)
        # Use database config for transcription

    # WebSocket handling (from websocket.py) - PER CONNECTION!
    async def handle_connect(self, connection_id: str):
        """Initialize new WebSocket connection"""
        self._connections[connection_id] = {
            'audio_buffer': b'',
            'config_id': None
        }

    async def handle_disconnect(self, connection_id: str):
        """Clean up WebSocket connection"""
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def handle_start_streaming(self, connection_id: str, config_id: int):
        """Start streaming - each connection MUST choose a config!"""
        if connection_id in self._connections:
            self._connections[connection_id]['config_id'] = config_id

    async def handle_audio_chunk(self, connection_id: str, data: bytes):
        """Process WebSocket audio chunks - each connection uses its chosen config!"""
        if connection_id not in self._connections:
            return
            
        self._connections[connection_id]['audio_buffer'] += data
        
        # Process buffered audio based on connection's chosen config
        config_id = self._connections[connection_id]['config_id']
        if not config_id:
            raise ValueError("Connection must choose a config before processing audio!")
        
        config = await self.get_by_id(config_id)
        # Use database config for transcription
```

### 3. NxSttRouter (routers/stt_router.py)
**ONE ROUTER HANDLES EVERYTHING - like MCP server!**
```python
from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.stt_service import NxSttService

@router("/stt", tags=["STT"])
class NxSttRouter(NxWebServerCrudRouter):
    # Inject ONE service (like MCP server!)
    stt_service: NxSttService = NxInject(NxSttService)

    # STT business logic endpoints
    @route("/upload", methods=["POST"])
    async def upload_audio(self, audio_file: UploadFile, config_id: int = None):
        """Handle file uploads for transcription"""
        return await self.stt_service.transcribe_file(audio_file, config_id)

    @route("/stream", methods=["GET"])
    async def get_stream_info(self):
        """Get WebSocket stream information"""
        return {"stream_url": "/stt/stream", "supported_formats": ["wav", "mp3", "flac"]}

    # CRUD operations for configurations (inherited from NxWebServerCrudRouter)
    # GET /stt/ - List all configurations
    # POST /stt/ - Create new configuration
    # GET /stt/{id} - Get configuration by ID
    # PUT /stt/{id} - Update configuration
    # DELETE /stt/{id} - Delete configuration
```

## Integration Points

### WebSocket Integration
- Uses existing `NxWebServerWebSocketService`
- Emits to rooms: `stt/{session_id}`
- Events: `transcription_update`, `streaming_started`, `streaming_stopped`

### Router Integration
- Uses existing `@router` decorator pattern
- Follows same pattern as `NxTemplateRouter`
- HTTP endpoints: `/stt/upload`

### Dependency Injection
- All services use `NxInject()` pattern
- Proper service lifecycle management
- Configuration-driven initialization

## Conversion Mapping

### Flask Routes → Plugin Routers
```
@app.route('/upload', methods=['POST'])  # Flask
↓
@route("/upload", methods=["POST"])      # Plugin
```

### Flask-SocketIO → Framework WebSocket
```
@socketio.on('audio_chunk')              # Flask-SocketIO
emit('transcription_update', data)       # Flask-SocketIO
↓
async def handle_audio_chunk(data, session_id)  # Plugin
await ws_service.send_ws_message(room, message) # Framework WS
```

### Global State → Service Injection
```
model = WhisperModel(...)                # Global (speech_recognition.py)
audio_buffer = b''                       # Global (websocket.py)
↓
self.model = WhisperModel(...)           # Single service instance
self.audio_buffer = b''                  # Single service instance
```

## Implementation Phases

### Phase 1: Plugin Setup
- [ ] Create `faster_backend/nonix_web_stt/` directory
- [ ] Create `plugin.json` with EMPTY config like MCP! 
- [ ] Implement `NxWebSttPlugin` with `@injectables` and `@web_routers` decorators
- [ ] NO `_startup()` method needed - like MCP server!

### Phase 2: Service & Router Migration
- [ ] Convert `speech_recognition.py` + `websocket.py` → SINGLE `NxSttService`
- [ ] NO initialize() method - load configs from database when needed
- [ ] Convert ALL transcription functions to async service methods
- [ ] Merge WebSocket buffering and CRUD operations into same service
- [ ] Use `NxInject()` for WebSocket service dependency
- [ ] Convert `routes.py` → `NxSttRouter` using `@router` decorator
- [ ] Add FastAPI request/response models and error handling

### Phase 3: Testing & Integration
- [ ] Test file upload transcription
- [ ] Test WebSocket real-time transcription
- [ ] Verify Vue.js frontend integration
- [ ] Add plugin to `main.py` PLUGINS list

## Configuration System

### Database Configuration Pattern
**All configuration stored in NxSttConfiguration table:**
```python
# NO plugin.json config - empty like MCP!
class NxSttService(BaseCrudService):
    async def transcribe_file(self, file_path: str, config_id: int = None) -> str:
        if config_id:
            # Load configuration from database
            config = await self.get_by_id(config_id)
            whisper_model = config.whisper_model
            device = config.device
            # Use database config for transcription
        else:
            # Use hardcoded defaults when no config specified
            whisper_model = "base"
            device = "cpu"
```

## API Endpoints

### HTTP Endpoints
- `POST /stt/upload` - Upload audio file for transcription

### WebSocket Events
- `start_streaming` → Initialize real-time session
- `audio_chunk` → Send audio data for transcription
- `stop_streaming` → End real-time session

### WebSocket Responses
- `streaming_started` - Session initialized
- `transcription_update` - Real-time transcription result
- `streaming_stopped` - Session ended

## Vue.js Integration Ready
- WebSocket channels already established
- Frontend can connect to `/stt/stream`
- POST files to `/stt/upload`
- Receive real-time transcription updates
- No conflicts with existing WebSocket infrastructure

## Key Benefits
- ✅ **Pure Backend Focus** - No frontend components
- ✅ **Simplified Architecture** - Single service handles all STT logic
- ✅ **Framework Integration** - Leverages existing infrastructure
- ✅ **Service Injection** - Proper DI patterns
- ✅ **Async Support** - Full async/await WebSocket handling
- ✅ **Scalability** - Multiple frontend clients supported
- ✅ **Consistency** - Follows NxWeb plugin patterns

## Dependencies
- `nonix_web` - HTTP routing and WebSocket services
- `faster-whisper` - Speech recognition engine
- `numpy` - Audio processing
- `torch` - ML framework (for Whisper)

## Critical Plugin Patterns (Follow PLUGIN.md Exactly!)

### ✅ CORRECT Patterns to Use

1. **Plugin Class Structure:**
```python
@injectables([NxSttService])
@web_routers([NxSttRouter])
class NxWebSttPlugin(BasePlugin):
    # ✅ NO methods needed - like MCP server!
    pass
```

2. **Service Configuration:**
```python
class NxSttService(BaseCrudService):
    # ✅ Load configs from database when needed
    async def transcribe_file(self, file_path: str, config_id: int = None):
        if config_id:
            config = await self.get_by_id(config_id)
            # Use database config
```

3. **Router Structure:**
```python
@router("/stt", tags=["STT"])
class NxSttRouter:
    service: NxSttService = NxInject(NxSttService)
```

### ❌ WRONG Patterns to Avoid

1. **Plugin Config Objects:**
```json
// ❌ WRONG - Don't add config to plugin.json!
"config": {
    "whisper_model": "base"
}
```

2. **Plugin Methods:**
```python
# ❌ WRONG - Don't add _startup() or _configure()
async def _startup(self, config):
    pass

# ❌ WRONG - Don't add initialize() to services  
async def initialize(self, config):
    pass
```

3. **Empty Constructors:**
```python
# ❌ WRONG - Don't add empty methods!
def __init__(self):
    super().__init__()
    # Nothing else
```

## Database Model & Schemas

### NxSttConfiguration Model (models/stt_configuration.py)
```python
from sqlalchemy import Boolean, Column, Integer, String
from nonix_web_db import BaseModel

class NxSttConfiguration(BaseModel):
    __tablename__ = 'stt_configurations'

    name = Column(String(255), unique=True, nullable=False)
    whisper_model = Column(String(50), default='base')
    device = Column(String(20), default='cpu')
    sample_rate = Column(Integer, default=16000)
    vad_enabled = Column(Boolean, default=False)
    language = Column(String(10))
    is_active = Column(Boolean, nullable=False, server_default='1')
```

### STT Configuration Schemas (schemas/stt_configuration_schemas.py)
```python
from pydantic import BaseModel, Field
from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel

class NxSttConfigurationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    whisper_model: str = 'base'
    device: str = 'cpu'
    sample_rate: int = 16000
    vad_enabled: bool = False
    language: Optional[str] = None
    is_active: bool = True

class NxSttConfigurationCreate(NxSttConfigurationBase):
    pass

class NxSttConfigurationUpdate(BaseUpdateModel, base_model=NxSttConfigurationBase):
    pass

class NxSttConfigurationInDbModel(NxSttConfigurationBase, BaseDbModelMixin):
    pass
```

## Notes
- All classes MUST start with `Nx` prefix
- SINGLE service handles ALL STT functionality (no separation needed)
- ONE table for configurations (like MCP server exactly)
- No global state - everything through DI
- WebSocket integration uses existing framework services
- Configuration-driven model loading
- Proper cleanup and error handling required
- Audio buffering and WebSocket events handled in same service
- Follow PLUGIN.md patterns exactly to avoid architectural issues
