# Nonix Plugin System - Usage Guide

## Overview

The Nonix Plugin System provides a powerful way to **load and manage plugins** in your application. It handles plugin discovery, dependency management, lifecycle control, and runtime configuration automatically.

**⚠️ Important Philosophy**: The plugin system is designed for **plugin loading and lifecycle management**, NOT for logic reuse through dependency injection. Plugins are loaders that expose functionality through the DI system. Most plugins should be accessed directly by name when needed, not injected globally.

## Dependencies

### Core Plugin System (Standalone)
- Plugin discovery and loading
- Plugin dependency management
- Plugin lifecycle management (configure/startup/shutdown)
- Configuration override

### Optional Advanced Features
- **Plugin Access** (`NxInjectPlugin`): For accessing other plugins by name (requires DI system)
- **Service Registration** (`@injectables`): For registering plugin services in DI (requires DI system)
- **Web Integration** (`@web_routers`): For automatic router registration (requires DI + Web system)

**Note**: Advanced features should be used sparingly. The standard pattern is direct plugin access by name when needed, and service injection by type for the functionality they expose.

## Quick Start

### 1. Create Your First Plugin

Create a new directory for your plugin with this structure:

```
my_plugin/
├── plugin.json
└── plugin.py
```

**plugin.json** - Plugin metadata and configuration:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "class": "MyPlugin",
  "dependencies": [],
  "config": {
    "database_url": "sqlite:///./app.db"
  }
}
```

**plugin.py** - Your plugin implementation:
```python
from nonix_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def _configure(self, config):
        # Plugin configuration happens here
        self.database_url = config.get("database_url")
        print(f"MyPlugin configured with DB: {self.database_url}")

    async def _startup(self, config):
        # Initialize resources (database connections, etc.)
        print("MyPlugin starting up...")

    async def _shutdown(self, config):
        # Clean up resources
        print("MyPlugin shutting down...")
```

### 2. Enable Your Plugin

Initialize the plugin manager and load your plugins:

```python
from nonix_plugin import NxPluginManager

# Create plugin manager with search paths
plugin_manager = NxPluginManager(["./plugins", "./"])

# Discover available plugins
plugin_manager.discover_plugins()

# Configure and start plugins
plugins_to_load = [
    {"name": "my-plugin"},
    # ... other plugins
]

plugin_manager.configure_plugins(plugins_to_load)
await plugin_manager.startup_plugins(plugins_to_load)
```

That's it! Your plugin will be automatically discovered, configured, and started.

## Plugin Configuration

### Basic Configuration

Every plugin needs a `plugin.json` file:

```json
{
  "name": "web-server",
  "version": "2.1.0",
  "class": "WebServerPlugin",
  "config": {
    "host": "localhost",
    "port": 8000
  }
}
```

### Runtime Configuration Override

Override plugin configuration when loading:

```python
plugins_to_load = [
    {
        "name": "web-server",
        "config": {
            "host": "0.0.0.0",
            "port": 8080
        }
    }
]

plugin_manager.configure_plugins(plugins_to_load)
```

### Dependency Management

Plugins can depend on other plugins:

```json
{
  "name": "user-auth",
  "version": "1.0.0",
  "class": "UserAuthPlugin",
  "dependencies": ["database", "web-server"],
  "config": {}
}
```

Dependencies are automatically loaded in the correct order.

## Plugin Lifecycle

### Configuration Phase
- Happens during application startup
- Override default configurations
- Set up middleware, routes, and mounts

### Startup Phase
- Initialize runtime resources
- Establish database connections
- Start background services
- Register event handlers

### Runtime Phase
- Plugin is fully operational
- Handle requests and events
- Interact with other plugins

### Shutdown Phase
- Clean up resources
- Close connections
- Save state if needed

## Accessing Other Plugins

### Plugin Access by Name (Requires DI Setup)

Plugins are accessed by name, not injected like services. Use `NxInjectPlugin` when you need to directly interact with another plugin:

```python
# First, set up DI system
from nonix_di.register import di_register
from nonix_plugin import NxPluginManager, NxInjectPlugin

# Create and register plugin manager in DI container
plugin_manager = NxPluginManager(["./plugins"])
di_register(NxPluginManager, instance=plugin_manager)

# Now you can access plugins by name
class MyPlugin(BasePlugin):
    # Access another plugin by name (not injection)
    database_plugin = NxInjectPlugin("database")

    def _configure(self, config):
        # Access the plugin directly when needed
        if self.database_plugin:
            self.db_connection = self.database_plugin.get_connection()
```

**Note**: `NxInjectPlugin` is for accessing plugins by name, not for dependency injection. Use this sparingly - most of the time you should access the services that plugins expose through regular DI injection.

### Direct Plugin Access (No DI Required)

Access plugins directly through the plugin manager:

```python
class MyPlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)
        self.plugin_manager = None

    def set_plugin_manager(self, manager):
        self.plugin_manager = manager

    def _configure(self, config):
        # Access other plugins directly
        if self.plugin_manager:
            database_plugin = self.plugin_manager.get_plugin("database")
            if database_plugin:
                self.db_connection = database_plugin.get_connection()
```

### Best Practice: Access Services, Not Plugins

Instead of accessing plugins directly, access the services they expose:

```python
# ❌ Don't access plugins for their functionality
database_plugin = NxInjectPlugin("database")
connection = database_plugin.get_connection()

# ✅ Access the services they register
db_service: DatabaseService = NxInject(DatabaseService)
connection = db_service.get_connection()
```

## Service Registration

### Plugins as Service Providers (Requires DI Setup)

Plugins act as **service providers** - they register services in the DI container that other parts of the application can inject. This is the primary way plugins expose their functionality:

```python
from nonix_di.decorator import injectables
from nonix_di.register import di_register
from nonix_plugin import BasePlugin

class DatabaseService:
    def get_connection(self):
        return "database_connection"

class CacheService:
    def get(self, key):
        return f"cached_value_{key}"

@injectables([DatabaseService, CacheService])
class DatabasePlugin(BasePlugin):
    async def _startup(self, config):
        # Plugin loads database/cache functionality
        # and exposes services for others to use
        print("Database services registered and available for injection")
```

### Consuming Registered Services

Other parts of the application inject the services that plugins provide:

```python
from nonix_di.resolve import NxInject

class UserService:
    # Inject services that plugins registered (by type)
    db_service: DatabaseService = NxInject(DatabaseService)
    cache_service: CacheService = NxInject(CacheService)

    def get_user_data(self, user_id):
        # Use services exposed by plugins
        connection = self.db_service.get_connection()
        cached_data = self.cache_service.get(f"user_{user_id}")
        return {"connection": connection, "cached": cached_data}
```

### Manual Service Registration

You can also register services manually during plugin lifecycle:

```python
from nonix_di.register import di_register
from nonix_plugin import BasePlugin

class MyPlugin(BasePlugin):
    async def _startup(self, config):
        # Register services manually
        db_service = DatabaseService()
        cache_service = CacheService()

        # Register instances in DI container for others to inject
        di_register(DatabaseService, instance=db_service)
        di_register(CacheService, instance=cache_service)
```

**Key Concept**: Plugins are loaders that register services. The services (not the plugins) are what gets injected by type throughout the application.

## Web Framework Integration

### Automatic Router Registration (Requires DI + Web)

Plugins can automatically register their web routes with the application:

```python
from fastapi import APIRouter
from nonix_web.decorator import web_routers
from nonix_plugin import BasePlugin

class ApiRouter:
    @staticmethod
    def to_router() -> APIRouter:
        router = APIRouter()
        router.add_api_route("/health", lambda: {"status": "ok"})
        router.add_api_route("/users", lambda: {"users": []})
        return router

@web_routers([ApiRouter])
class WebPlugin(BasePlugin):
    def _configure(self, config):
        # Router is automatically registered with the web server
        pass
```

### Custom Router Prefix

```python
@web_routers([ApiRouter], prefix="/v1/api")
class V1ApiPlugin(BasePlugin):
    # Routes will be available at /v1/api/health, /v1/api/users
    pass
```

## Common Usage Patterns

### Database Plugin Pattern

```python
class DatabasePlugin(BasePlugin):
    def _configure(self, config):
        self.connection_string = config.get("url")

    async def _startup(self, config):
        self.engine = create_async_engine(self.connection_string)
        # Create tables, run migrations

    async def _shutdown(self, config):
        await self.engine.dispose()

    def get_session(self):
        return self.engine.session()
```

### Web Service Plugin Pattern

```python
class WebServicePlugin(BasePlugin):
    def _configure(self, config):
        self.app = config.get("app")  # FastAPI app instance
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/api/health")
        async def health_check():
            return {"status": "healthy"}
```

### Background Service Plugin Pattern

```python
class BackgroundServicePlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)
        self.tasks = []

    async def _startup(self, config):
        # Start background tasks
        task = asyncio.create_task(self.process_queue())
        self.tasks.append(task)

    async def _shutdown(self, config):
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
```

## Plugin Discovery

Plugins are automatically discovered from specified search paths:

```python
# Create plugin manager with search paths
plugin_manager = NxPluginManager([
    "./plugins",           # Local plugins directory
    "/opt/myapp/plugins",  # System plugins
    "./"                   # Current directory
])
```

The system scans for directories containing `plugin.json` files.

## Configuration Management

### Environment-Based Configuration

```json
{
  "name": "database",
  "config": {
    "url": "${DATABASE_URL:sqlite:///./app.db}",
    "pool_size": "${DB_POOL_SIZE:10}"
  }
}
```

### Conditional Configuration

```python
class ConditionalPlugin(BasePlugin):
    def _configure(self, config):
        if config.get("enable_feature"):
            self.setup_feature()
        else:
            self.disable_feature()
```

## Error Handling

### Plugin Load Failures

Failed plugins are logged but don't stop the application. Check logs for:
- Missing dependencies
- Configuration errors
- Import failures

### Runtime Error Handling

```python
class RobustPlugin(BasePlugin):
    async def _startup(self, config):
        try:
            await self.connect_to_service()
        except ConnectionError:
            self.logger.error("Service unavailable, running in degraded mode")
            self.degraded_mode = True
```

## Best Practices

### 1. Plugin Naming
Use descriptive, unique names:
- ✅ `user-authentication`
- ✅ `payment-processor`
- ❌ `plugin1`
- ❌ `myplugin`

### 2. Configuration Design
Make plugins configurable:
```json
{
  "config": {
    "timeout": 30,
    "retries": 3,
    "debug": false
  }
}
```

### 3. Dependency Declaration
Always declare dependencies explicitly:
```json
{
  "dependencies": ["database", "cache", "logger"]
}
```

### 4. Resource Management
Always clean up in shutdown:
```python
async def _shutdown(self, config):
    await self.close_connections()
    await self.save_state()
```

### 5. Error Handling
Handle failures gracefully:
```python
async def _startup(self, config):
    try:
        await self.initialize()
    except Exception as e:
        self.logger.error(f"Startup failed: {e}")
        raise
```

## Advanced Features

### Plugin Callbacks

Add custom lifecycle callbacks:

```python
from nonix_plugin import add_startup_callback, add_shutdown_callback

def my_custom_startup(plugin, config):
    print(f"Custom startup for {plugin.name}")

def my_custom_shutdown(plugin, config):
    print(f"Custom shutdown for {plugin.name}")

# Apply to plugin class
add_startup_callback(MyPlugin, my_custom_startup)
add_shutdown_callback(MyPlugin, my_custom_shutdown)
```

### Circular Dependency Detection

The system automatically detects and prevents circular dependencies:

```json
// ❌ This will fail
{"name": "a", "dependencies": ["b"]}
{"name": "b", "dependencies": ["a"]}

// ✅ This works
{"name": "a", "dependencies": ["b"]}
{"name": "b", "dependencies": []}
```

## Troubleshooting

### Plugin Not Loading
Check:
- `plugin.json` exists and is valid JSON
- Plugin directory is in search path
- All dependencies are available
- Class name matches in `plugin.json`

### Configuration Not Applied
Check:
- Configuration keys match exactly
- JSON syntax is correct
- Runtime overrides use correct structure

### Dependency Issues
Check:
- All dependencies are listed in `plugin.json`
- Dependencies are available in search paths
- No circular dependencies exist

## Example Application Setup

### Standalone Usage (Core Features Only)

For basic plugin functionality without DI or web integration:

```python
import asyncio
from nonix_plugin import NxPluginManager

async def main():
    # Create and configure plugin manager
    plugin_manager = NxPluginManager(["./plugins", "./"])

    # Discover available plugins
    plugin_manager.discover_plugins()

    # Define plugins to load
    plugins_to_load = [
        {"name": "database"},
        {"name": "logger"},
        {
            "name": "cache",
            "config": {
                "ttl": 3600,
                "max_size": 1000
            }
        }
    ]

    try:
        # Configure and start plugins
        plugin_manager.configure_plugins(plugins_to_load)
        await plugin_manager.startup_plugins(plugins_to_load)

        # Your application logic here
        print("Application running with plugins...")

        # Keep application running
        await asyncio.sleep(float('inf'))

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Clean shutdown
        await plugin_manager.shutdown_plugins()

if __name__ == "__main__":
    asyncio.run(main())
```

### Full Integration with DI and Web Framework

For complete plugin functionality with DI injection and web integration:

```python
import asyncio
from fastapi import FastAPI
from nonix_di.register import di_register
from nonix_plugin import NxPluginManager

# Set up FastAPI app
app = FastAPI(title="My Plugin App")

async def main():
    # Register app in DI container
    di_register(FastAPI, instance=app)

    # Create and register plugin manager in DI container
    plugin_manager = NxPluginManager(["./plugins"])
    di_register(NxPluginManager, instance=plugin_manager)

    # Discover available plugins
    plugin_manager.discover_plugins()

    # Define plugins to load
    plugins_to_load = [
        {"name": "database"},
        {"name": "auth"},
        {
            "name": "api-gateway",
            "config": {
                "rate_limit": 1000,
                "cors_origins": ["*"]
            }
        }
    ]

    try:
        # Configure and start plugins (this also registers services via @injectables)
        plugin_manager.configure_plugins(plugins_to_load)
        await plugin_manager.startup_plugins(plugins_to_load)

        print("Application running with plugins...")

        # Keep application running
        await asyncio.sleep(float('inf'))

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Clean shutdown
        await plugin_manager.shutdown_plugins()

if __name__ == "__main__":
    asyncio.run(main())
```

### Web Framework Integration with Lifespan

For web applications with proper startup/shutdown:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from nonix_di.register import di_register
from nonix_plugin import NxPluginManager

app = FastAPI(title="Plugin Web App")
plugin_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    global plugin_manager

    # Register app in DI container
    di_register(FastAPI, instance=app)

    # Create and register plugin manager
    plugin_manager = NxPluginManager(["./plugins"])
    di_register(NxPluginManager, instance=plugin_manager)

    # Initialize plugins
    plugin_manager.discover_plugins()
    plugins_to_load = [{"name": "database"}, {"name": "auth"}]
    plugin_manager.configure_plugins(plugins_to_load)
    await plugin_manager.startup_plugins(plugins_to_load)

    yield

    # Cleanup
    await plugin_manager.shutdown_plugins()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Application with plugins"}
```

## Choosing the Right Setup

### For Simple Applications
Use the **Standalone Usage** example when you only need:
- Plugin discovery and loading
- Basic dependency management
- Configuration override

### For Complex Applications
Use the **Full Integration** examples when you need:
- Plugin injection (`NxInjectPlugin`)
- Service registration (`@injectables`)
- Cross-plugin communication
- Web framework integration

### For Web Applications
Use the **Web Framework Integration** example when you need:
- Automatic router registration
- Web server lifecycle management
- HTTP endpoint integration

The setup you choose depends on your application's complexity and whether you need advanced DI features.

## Complete Integration Example

Here's how plugins work as loaders that expose functionality through the DI system:

```python
from fastapi import APIRouter
from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_web.decorator import web_routers
from nonix_plugin import BasePlugin, NxInjectPlugin

# Service classes that the plugin will register in DI
class DatabaseService:
    def get_data(self):
        return {"data": "from database"}

class CacheService:
    def get_cached(self, key):
        return f"cached_{key}"

# Router class for web endpoints that the plugin exposes
class ApiRouter:
    @staticmethod
    def to_router() -> APIRouter:
        router = APIRouter()
        router.add_api_route("/data", lambda: {"message": "Hello from plugin!"})
        return router

# Plugin as a LOADER - it exposes functionality, doesn't get injected
@web_routers([ApiRouter])
@injectables([DatabaseService, CacheService])
class DatabasePlugin(BasePlugin):
    async def _startup(self, config):
        # Plugin loads and exposes functionality
        # - Web routes registered at /api/data
        # - Services registered in DI container for others to use
        print("Database plugin loaded and exposed services/routes")
```

Now other parts of the application can inject the services:

```python
# Other services can inject the exposed functionality
class UserService:
    # Inject services exposed by plugins (by type)
    db_service: DatabaseService = NxInject(DatabaseService)
    cache_service: CacheService = NxInject(CacheService)

    def get_user_data(self, user_id):
        # Use services that plugins exposed
        data = self.db_service.get_data()
        cached = self.cache_service.get_cached(f"user_{user_id}")
        return {"user_data": data, "cached": cached}

# Other plugins can access this plugin by name if needed
class ApiPlugin(BasePlugin):
    # Rarely needed - access by name only when necessary
    db_plugin = NxInjectPlugin("database")

    def _configure(self, config):
        # Only access plugin directly when you need plugin-specific methods
        if self.db_plugin:
            # Plugin-specific operations
            pass
```

## Key Principles

### Plugins vs Services
- **Plugins** = Loaders that expose functionality
- **Services** = The actual functionality that gets injected
- **Injection** = Services by type, Plugins by name (rarely)

### When to Use What
- **NxInject(ServiceClass)**: Most common - inject services that plugins expose
- **NxInjectPlugin("plugin-name")**: Rare - only when you need plugin-specific methods
- **Direct plugin access**: Very rare - use service injection instead

### The Flow
1. **Plugin loads** → Registers services/routes in DI system
2. **Application injects services** → Uses functionality by type
3. **Occasional plugin access** → Gets plugin by name when needed

**Remember**: Plugins are loaders, not injectable components. They expose functionality through the DI system for others to use.

## Plugin Development Workflow

1. **Design** - Plan your plugin's purpose and dependencies
2. **Create** - Set up directory structure and files
3. **Configure** - Write `plugin.json` with metadata
4. **Implement** - Code your plugin class with lifecycle methods
5. **Test** - Add to application configuration and test
6. **Deploy** - Package and distribute your plugin

The Nonix Plugin System makes it easy to build modular, maintainable applications with clean separation of concerns and automatic dependency management.
