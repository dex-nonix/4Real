# AI_README: Nonix Daemon System API

## Requirements
- Python 3.8+
- nonix_plugin
- nonix_di
- pyee

## Core Classes & Interfaces

### Daemon Base Classes
```python
class NxBaseDaemon:
    """Abstract base class for all daemon types"""
    def __init__(self, name: str) -> None
    async def start(self) -> None: """Start daemon with event emission"""
    async def stop(self) -> None: """Stop daemon with event emission"""
    @abstractmethod
    async def _start(self) -> None: """Implementation of start logic"""
    @abstractmethod
    async def _stop(self) -> None: """Implementation of stop logic"""
    @abstractmethod
    async def _run(self) -> None: """Main daemon loop implementation"""
    # Public attributes
    name: str
    logger: logging.Logger
    emitter: pyee_asyncio.AsyncIOEventEmitter

class NxAsyncioDaemon(NxBaseDaemon):
    """Async I/O background tasks in same process"""
    def __init__(self, name: str) -> None
    async def _start(self) -> None: """Create and start asyncio task"""
    async def _stop(self) -> None: """Cancel asyncio task"""
    @abstractmethod
    async def _run(self) -> None: """Main daemon loop implementation"""

class NxThreadDaemon(NxBaseDaemon):
    """CPU-bound tasks in separate thread"""
    def __init__(self, name: str) -> None
    async def _start(self) -> None: """Create and start thread"""
    async def _stop(self) -> None: """Stop thread and join"""
    @abstractmethod
    async def _run(self) -> None: """Main daemon loop implementation"""

class NxProcessDaemon(NxBaseDaemon):
    """Memory-heavy tasks in separate process"""
    def __init__(self, name: str) -> None
    async def _start(self) -> None: """Create and start process"""
    async def _stop(self) -> None: """Terminate process and join"""
    @abstractmethod
    async def _run(self) -> None: """Main daemon loop implementation"""
```

### Daemon Manager
```python
class NxDaemonManager:
    """Manages all registered daemons"""
    def __init__(self) -> None
    def add_daemon(self, daemon: NxBaseDaemon) -> None: """Add daemon to manager"""
    def remove_daemon(self, name: str) -> None: """Remove daemon from manager"""
    async def start_all(self) -> None: """Start all registered daemons"""
    async def stop_all(self) -> None: """Stop all registered daemons"""
    # Public attributes
    daemons: Dict[str, NxBaseDaemon]
    logger: logging.Logger
    emitter: pyee_asyncio.AsyncIOEventEmitter
```

### Events
```python
class NxDaemonEvents:
    """Daemon lifecycle events"""
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    ERROR = "error"

class NxDaemonManagerEvents:
    """Manager events"""
    DAEMON_ADDED = "daemon_added"
    DAEMON_REMOVED = "daemon_removed"
    BEFORE_START_ALL = "before_start_all"
    AFTER_START_ALL = "after_start_all"
    BEFORE_STOP_ALL = "before_stop_all"
    AFTER_STOP_ALL = "after_stop_all"
    MANAGER_ERROR = "manager_error"
```

## Decorators
```python
def daemons(classes: list) -> Callable:
    """Register daemon classes with plugin system"""
```

## Integration Points
```python
# Inject daemon manager
from nonix_di import NxInject
daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

# Register daemons in plugin
@daemons([MyAsyncioDaemon, MyThreadDaemon])
class MyPlugin(BasePlugin):
    pass

# Event handling
daemon.emitter.on(NxDaemonEvents.AFTER_START.value, callback)
daemon_manager.emitter.on(NxDaemonManagerEvents.AFTER_START_ALL.value, callback)

# Enable daemon system
settings.PLUGINS = [{"name": "daemon"}]
```

## Configuration Schema
```json
{
  "name": "daemon",
  "class": "NxDaemonPlugin",
  "dependencies": []
}
```
