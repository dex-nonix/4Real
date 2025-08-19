# Generic WebSocket System Infrastructure

## Overview

The Generic WebSocket System provides real-time communication infrastructure for any service that needs it. It's a complete WebSocket extension to BaseApiService with `@expose_ws` decorators and dynamic channel mapping.

## Architecture

### 1. WebSocket Endpoint
- **Path**: `/api/ws/` (single WebSocket connection)
- **Protocol**: SocketIO
- **Purpose**: Single connection point for all WebSocket communication

### 2. Channel-Based Routing
- **Pattern**: `@expose_ws('channel/path/{params}')`
- **Functionality**: 
  - Receive POST messages to channel (like HTTP endpoint)
  - Emit events to specific channel (NO broadcasting)
- **Dynamic Mapping**: Flask-style path parameters with placeholders

## Implementation

### Backend: @expose_ws Decorator

```python
def expose_ws(channel: str) -> Callable:
    """Mark method as WebSocket channel handler."""
    
    def decorator(func: Callable) -> Callable:
        setattr(func, '_expose_ws', True)
        setattr(func, '_channel', channel)
        return func
    
    return decorator
```

### Add WebSocket Methods to Existing BaseApiService

**ADD these methods to your existing `BaseApiService` class in `backend/app/services/base_api_service.py`:**

```python
# ADD TO: backend/app/services/base_api_service.py

def __init__(self):
    """Initialize WebSocket integration."""
    self._socketio = None  # Will be set by APIRouter during registration

def set_socketio(self, socketio_instance):
    """Set SocketIO instance for WebSocket communication."""
    self._socketio = socketio_instance

def send_to_channel(self, channel: str, event: str, data: dict, room: str = None):
    """
    Send event to a specific WebSocket channel.
    
    Args:
        channel: Channel path (e.g., 'service/channel/123')
        event: Event name (e.g., 'status_updated')
        data: Event data payload
        room: Optional room name (defaults to channel)
    """
    if not self._socketio:
        print(f"Warning: SocketIO not initialized for {self.__class__.__name__}")
        return
    
    # Use channel as room if no specific room provided
    target_room = room or channel
    
    # Emit event to specific room (NO broadcasting!)
    self._socketio.emit(f'{channel}:{event}', data, room=target_room)

def send_to_room(self, room: str, event: str, data: dict):
    """
    Send event to a specific room.
    
    Args:
        room: Room name (e.g., 'service/room/123')
        event: Event name (e.g., 'notification')
        data: Event data payload
    """
    if not self._socketio:
        print(f"Warning: SocketIO not initialized for {self.__class__.__name__}")
        return
    
    # Emit event to specific room
    self._socketio.emit(event, data, room=room)

def get_exposed_ws_methods(self) -> List[Dict[str, Any]]:
    """Get all @expose_ws methods with their metadata."""
    exposed_ws_methods = []
    
    for attr_name in dir(self):
        method = getattr(self, attr_name)
        if callable(method) and hasattr(method, '_expose_ws'):
            method_info = {
                'name': attr_name,
                'channel': getattr(method, '_channel'),
                'summary': getattr(method, '_summary'),
                'description': getattr(method, '_description')
            }
            exposed_ws_methods.append(method_info)
    
    return exposed_ws_methods
```

### Generic Service Method Example

```python
class GenericService(BaseApiService):
    @expose_ws('service/{service_id}/channel')
    def service_channel(self, data: dict, service_id: int):
        """Handle WebSocket messages to service channel."""
        
        # Process incoming message
        result = self.process_message(data, service_id)
        
        # Emit event using BaseApiService method
        self.send_to_channel(
            channel=f'service/{service_id}/channel',
            event='message_processed',
            data={'result': result}
        )
        
        return {'status': 'success'}
```

### WebSocket Event Handler

```python
@socketio.on('channel_message')
def handle_channel_message(data):
    """Route incoming channel messages to appropriate @expose_ws methods."""
    
    channel = data.get('channel')
    message_data = data.get('data')
    
    # Find which @expose_ws method handles this channel
    for service_name, service in registered_services.items():
        for attr_name in dir(service):
            method = getattr(service, attr_name)
            if hasattr(method, '_expose_ws'):
                if channel_matches(method._channel, channel):
                    # Call the service method (like POST endpoint)
                    return method(message_data, **extract_params(channel, method._channel))
    
    return {'error': 'Channel not found'}
```

## Service Integration Pattern

### 1. All Services Already Inherit from BaseApiService

```python
# Any service can inherit and use WebSocket capabilities
class AnyService(BaseApiService):
    """Generic service with optional WebSocket support."""
    
    # Optional: Use @expose_ws for WebSocket channels
    @expose_ws('service/{id}/updates')
    def service_updates_channel(self, data: dict, id: int):
        """WebSocket channel for service updates."""
        # ... implementation
    
    # Optional: Use generic WebSocket methods to emit events
    def some_method(self):
        # Emit event to any channel
        self.send_to_channel('some/channel', 'event_name', data)
```

### 2. Automatic WebSocket Integration

```python
# APIRouter automatically sets SocketIO instance for all services
class APIRouter:
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.services = {}
    
    def register_service(self, service_name: str, service_instance: BaseApiService):
        """Register service and enable WebSocket capabilities."""
        # Set SocketIO instance for WebSocket communication
        service_instance.set_socketio(self.socketio)
        
        # Register service
        self.services[service_name] = service_instance
        
        # Discover both HTTP and WebSocket endpoints
        self._discover_http_endpoints(service_instance)
        self._discover_websocket_channels(service_instance)
    
    def _discover_websocket_channels(self, service: BaseApiService):
        """Discover @expose_ws methods and register WebSocket channels."""
        ws_methods = service.get_exposed_ws_methods()
        
        for method_info in ws_methods:
            channel = method_info['channel']
            print(f"Registered WebSocket channel: {channel}")
```

## Generic Channel Patterns

### 1. Service Channels
```
service/{service_id}/channel
├── Receive: POST message to service channel
├── Emit: service/{service_id}/channel:event_name
└── Emit: service/{service_id}/channel:status_updated
```

### 2. Generic Update Channels
```
updates/{entity_type}/{entity_id}
├── Receive: POST update request
├── Emit: updates/{entity_type}/{entity_id}:updated
└── Emit: updates/{entity_type}/{entity_id}:deleted
```

### 3. Notification Channels
```
notifications/{user_id}
├── Receive: POST notification
├── Emit: notifications/{user_id}:received
└── Emit: notifications/{user_id}:read
```

## Frontend Usage

### 1. Send Message to Channel (POST)

```javascript
// Send message to any service channel
socket.emit('channel_message', {
    channel: 'service/123/channel',
    data: { 
        message: 'Hello service',
        user_id: 456
    }
})

// Send update request
socket.emit('channel_message', {
    channel: 'updates/entity/789',
    data: {
        action: 'update',
        data: { name: 'New Name' }
    }
})
```

### 2. Listen to Channel Events

```javascript
// Listen for events from any service channel
socket.on('service/123/channel:event_name', (data) => {
    console.log('Event received:', data)
})

socket.on('updates/entity/789:updated', (data) => {
    console.log('Entity updated:', data)
})
```

## Key Principles

### 1. NO Broadcasting
- **Events are channel-scoped** - Only clients subscribed to specific channel receive events
- **Room-based isolation** - Automatic client separation by channel
- **Secure communication** - No cross-channel data leakage

### 2. POST + Events Pattern
- **Send messages** - Like POST to HTTP endpoint
- **Receive events** - From specific channel
- **Bidirectional** - Client can send and receive on same channel
- **Consistent** - Same pattern as @expose HTTP endpoints

### 3. Dynamic Channel Mapping
- **Path parameters** - Flask-style {param} placeholders
- **Auto-discovery** - @expose_ws methods automatically registered
- **Flexible routing** - Easy to add new channels
- **Parameter extraction** - Automatic path parameter parsing

### 4. Generic Service Architecture
- **Single inheritance** - All services already inherit from BaseApiService
- **Optional WebSocket** - Services choose whether to use WebSocket
- **Shared capabilities** - WebSocket methods available to all services
- **Consistent patterns** - Same decorator style and parameter handling

## Database Integration

### 1. Channel Registration
```python
# Channels are discovered automatically from @expose_ws decorators
# No manual registration required
# No database tables for channels
```

### 2. Event Logging (Optional)
```python
# Can log channel events to database for audit
# Each service decides what to log
# No centralized event logging required
```

## Security & Isolation

### 1. Channel Access Control
- **Room-based isolation** - Clients only see their subscribed channels
- **Parameter validation** - Path parameters validated before method execution
- **Service-level security** - Same security as HTTP endpoints

### 2. Client Management
- **Automatic room assignment** - Based on channel subscription
- **Connection cleanup** - Automatic room cleanup on disconnect
- **Session persistence** - Maintains channel subscriptions across reconnects

## Implementation Status

### ✅ Completed
- [ ] WebSocket endpoint setup (`/api/ws/`)
- [ ] @expose_ws decorator implementation
- [ ] Channel message routing system
- [ ] Service method integration
- [ ] Frontend SocketIO client setup
- [ ] Channel subscription management

### 🔄 In Progress
- [ ] Generic WebSocket infrastructure
- [ ] Channel discovery system
- [ ] Service integration framework

### 📋 Next Steps
1. Implement @expose_ws decorator
2. Set up Flask-SocketIO integration
3. Create channel message router
4. Add WebSocket methods to BaseApiService
5. Test generic channel system
6. Document service integration patterns

## Benefits

### 1. Consistent Architecture
- **Same pattern** - As @expose HTTP endpoints
- **Same services** - Reuse existing service methods
- **Same security** - Same access control mechanisms

### 2. Real-time Updates
- **Live status updates** - Any service can emit real-time events
- **Live notifications** - Instant delivery of important updates
- **Live presence** - User activity updates

### 3. Scalable Design
- **Channel isolation** - No cross-talk between channels
- **Room-based** - Automatic client management
- **Dynamic** - Easy to add new channels
- **Efficient** - Single WebSocket connection per client

### 4. Developer Experience
- **Familiar patterns** - Same as existing @expose decorators
- **Automatic discovery** - No manual channel registration
- **Unified service class** - HTTP + WebSocket in same service
- **Simple WebSocket calls** - `self.send_to_channel()` method

## Generic Use Cases

### 1. Service Status Updates
```python
class GenericService(BaseApiService):
    @expose_ws('service/{service_id}/status')
    def status_channel(self, data: dict, service_id: int):
        """Handle status update requests."""
        
        # Process status update
        new_status = self.update_status(data, service_id)
        
        # Emit status change event
        self.send_to_channel(
            channel=f'service/{service_id}/status',
            event='status_changed',
            data={'status': new_status}
        )
        
        return {'status': 'success'}
```

### 2. Entity Update Notifications
```python
class GenericService(BaseApiService):
    @expose_ws('entity/{entity_type}/{entity_id}/updates')
    def entity_updates_channel(self, data: dict, entity_type: str, entity_id: int):
        """Handle entity update notifications."""
        
        # Process entity update
        updated_entity = self.update_entity(data, entity_type, entity_id)
        
        # Emit update notification
        self.send_to_channel(
            channel=f'entity/{entity_type}/{entity_id}/updates',
            event='entity_updated',
            data={'entity': updated_entity}
        )
        
        return {'status': 'success'}
```

This generic WebSocket system provides a complete infrastructure that any service can use for real-time communication, with automatic channel discovery and consistent patterns across all services.
