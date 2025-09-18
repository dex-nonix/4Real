# Nonix Plugin System - Usage Guide

## Overview

The Nonix Plugin System provides a powerful, flexible way to extend and customize your application through modular plugins. It handles plugin discovery, dependency management, lifecycle control, and runtime configuration automatically.

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

Use dependency injection to access other plugins:

```python
from nonix_plugin import NxInjectPlugin

class MyPlugin(BasePlugin):
    # Inject another plugin
    database_plugin = NxInjectPlugin("database")

    def _configure(self, config):
        # Access the injected plugin
        if self.database_plugin:
            self.db_connection = self.database_plugin.get_connection()
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

### Standalone Usage

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
        {"name": "web-server"},
        {"name": "user-auth"},
        {
            "name": "api-gateway",
            "config": {
                "rate_limit": 1000,
                "cors_origins": ["*"]
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

### Integration with Web Frameworks

You can also integrate the plugin system with any web framework:

```python
from fastapi import FastAPI
from nonix_plugin import NxPluginManager

app = FastAPI()
plugin_manager = NxPluginManager(["./plugins"])

@app.on_event("startup")
async def startup_event():
    plugin_manager.discover_plugins()
    plugins_to_load = [{"name": "database"}, {"name": "auth"}]
    plugin_manager.configure_plugins(plugins_to_load)
    await plugin_manager.startup_plugins(plugins_to_load)

@app.on_event("shutdown")
async def shutdown_event():
    await plugin_manager.shutdown_plugins()

@app.get("/")
async def root():
    return {"message": "Application with plugins"}
```

This setup will automatically:
1. Discover all plugins in `./plugins`
2. Load plugins in dependency order
3. Configure each plugin with its config
4. Start all plugins
5. Run your application

## Plugin Development Workflow

1. **Design** - Plan your plugin's purpose and dependencies
2. **Create** - Set up directory structure and files
3. **Configure** - Write `plugin.json` with metadata
4. **Implement** - Code your plugin class with lifecycle methods
5. **Test** - Add to application configuration and test
6. **Deploy** - Package and distribute your plugin

The Nonix Plugin System makes it easy to build modular, maintainable applications with clean separation of concerns and automatic dependency management.
