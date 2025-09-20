# AI_README: Nonix Plugin System API

## Requirements
- Python 3.8+
- No external dependencies

## Core Classes & Interfaces

### Base Plugin
```python
class BasePlugin:
    """Abstract base class for all plugins"""
    def __init__(self, config: Dict[str, Any]) -> None
    def configure(self, config: Dict[str, Any]) -> None: """Configure plugin with final config"""
    async def startup(self, config: Dict[str, Any]) -> None: """Start plugin with runtime resources"""
    async def shutdown(self, config: Dict[str, Any]) -> None: """Shutdown plugin and cleanup resources"""
    def _configure(self, config: Dict[str, Any]) -> None: """Override for configuration logic"""
    async def _startup(self, config: Dict[str, Any]) -> None: """Override for startup logic"""
    async def _shutdown(self, config: Dict[str, Any]) -> None: """Override for shutdown logic"""
    # Public attributes
    name: str
    version: str
    config: Dict[str, Any]
    plugin_dir: Path
    _logger: logging.Logger
```

### Plugin Manager
```python
class NxPluginManager:
    """Manages plugin discovery, loading and lifecycle"""
    def __init__(self, plugin_paths: Union[str, List[str]]) -> None
    def discover_plugins(self) -> None: """Scan directories for plugin.json files"""
    def configure_plugins(self, plugins_to_load: List[Union[str, Dict[str, Any]]]) -> None: """Configure plugins in dependency order"""
    async def startup_plugins(self, plugins_to_load: List[Union[str, Dict[str, Any]]]) -> None: """Start plugins in dependency order"""
    async def shutdown_plugins(self) -> None: """Shutdown all plugins in reverse order"""
    def get_plugin(self, name: str) -> BasePlugin | None: """Get loaded plugin by name"""
    # Public attributes
    plugin_paths: List[Path]
    available_plugins: Dict[str, Dict[str, Any]]
    loaded_plugins: Dict[str, BasePlugin]
```

### Plugin Injection
```python
class NxInjectPlugin(Generic[T]):
    """Property descriptor for plugin access by name"""
    def __init__(self, dependency: str | Callable[[], str], required: bool = True) -> None
    def __get__(self, instance, owner) -> T | None: """Resolve plugin on first access"""
    # Public attributes
    dependency: str | Callable[[], str]
    required: bool
    plugin_manager: NxPluginManager
```

## Functions
```python
def add_configure_callback(plugin_class: Type[BasePlugin], callback: Callable, args: Any = None, kwargs: Any = None) -> Type[BasePlugin]:
    """Add configuration callback to plugin class"""

def add_startup_callback(plugin_class: Type[BasePlugin], callback: Callable, args: Any = None, kwargs: Any = None) -> Type[BasePlugin]:
    """Add startup callback to plugin class"""

def add_shutdown_callback(plugin_class: Type[BasePlugin], callback: Callable, args: Any = None, kwargs: Any = None) -> Type[BasePlugin]:
    """Add shutdown callback to plugin class"""
```

## Integration Points
```python
# Create plugin manager
plugin_manager = NxPluginManager(["./plugins", "./"])
plugin_manager.discover_plugins()

# Configure and start plugins
plugins_to_load = [
    {"name": "database", "config": {"url": "sqlite:///./app.db"}},
    {"name": "web-server"}
]
plugin_manager.configure_plugins(plugins_to_load)
await plugin_manager.startup_plugins(plugins_to_load)

# Access loaded plugins
db_plugin = plugin_manager.get_plugin("database")

# Plugin injection (requires DI setup)
class MyPlugin(BasePlugin):
    db_plugin = NxInjectPlugin("database")
    optional_plugin = NxInjectPlugin("optional", required=False)

# Custom callbacks
@add_startup_callback
def my_startup(plugin, config):
    print(f"Starting {plugin.name}")

@add_shutdown_callback
def my_shutdown(plugin, config):
    print(f"Stopping {plugin.name}")
```

## Configuration Schema
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "class": "MyPlugin",
  "module": "plugin",
  "dependencies": ["other-plugin"],
  "config": {
    "setting1": "value1",
    "setting2": 42
  }
}
```
