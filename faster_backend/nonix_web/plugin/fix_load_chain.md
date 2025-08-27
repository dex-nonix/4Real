# Fix Plugin Loading Chain - 3-Step System

## The Problem

Currently, all plugins load during the FastAPI lifespan startup, but middleware must be added **before** the lifespan begins. This causes the error:

```
Cannot add middleware after an application has started
```

## The Solution: 3-Step Plugin Loading

We need to split plugin loading into 3 phases:

1. **`configure()`** - App structure setup (BEFORE lifespan starts)
2. **`startup()`** - Runtime initialization (DURING lifespan startup)  
3. **`shutdown()`** - Cleanup (DURING lifespan shutdown)

## What Files to Change

### 1. **`faster_backend/nonix_web/plugin/base_plugin.py`**

**Replace the current methods with:**

```python
class BasePlugin(ABC):
    api_services = []

    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    async def configure(self, server: "NxWebServer", config: Dict[str, Any]):
        """Configure app structure: middleware, routes, static files"""
        for routed_service in self.api_services:
            server.include_router(routed_service.to_router(server), prefix="/api")

    async def startup(self, server: "NxWebServer", config: Dict[str, Any]):
        """Runtime startup: database connections, async initialization"""
        pass

    async def shutdown(self, server: "NxWebServer", config: Dict[str, Any]):
        """Cleanup: close connections, dispose resources"""
        pass
```

**Remove:** `async def load_plugin()` and `async def _load_plugin()`

### 2. **`faster_backend/nonix_web/plugin/plugin_manager.py`**

**Add these new methods:**

```python
def configure_plugins(self, plugins_to_load: List[Union[str, Dict[str, Any]]]):
    """Configure all plugins (app structure) - called before lifespan"""
    self._logger.info("Starting to configure plugins...")
    load_order = self._resolve_dependencies(plugins_to_load)
    
    for plugin_info in load_order:
        plugin_name = plugin_info if isinstance(plugin_info, str) else plugin_info.get("name")
        if not plugin_name or plugin_name in self.loaded_plugins:
            continue
            
        override_config = plugin_info.get("config", {}) if isinstance(plugin_info, dict) else {}
        plugin_data = self.available_plugins.get(plugin_name)
        if not plugin_data:
            continue
            
        await self._configure_plugin(plugin_name, plugin_data, override_config)

async def startup_plugins(self, plugins_to_load: List[Union[str, Dict[str, Any]]]):
    """Startup all plugins (runtime) - called during lifespan startup"""
    self._logger.info("Starting plugin runtime initialization...")
    load_order = self._resolve_dependencies(plugins_to_load)
    
    for plugin_info in load_order:
        plugin_name = plugin_info if isinstance(plugin_info, str) else plugin_info.get("name")
        if not plugin_name or plugin_name not in self.loaded_plugins:
            continue
            
        plugin_instance = self.loaded_plugins[plugin_name]
        await plugin_instance.startup(self.server, plugin_instance.config)

async def shutdown_plugins(self):
    """Shutdown all plugins (cleanup) - called during lifespan shutdown"""
    self._logger.info("Starting plugin cleanup...")
    
    for plugin_name, plugin_instance in reversed(list(self.loaded_plugins.items())):
        await plugin_instance.shutdown(self.server, plugin_instance.config)
```

**Add this helper method:**

```python
async def _configure_plugin(self, plugin_name: str, plugin_data: Dict[str, Any], override_config: Dict[str, Any]):
    """Configure a single plugin (creates instance and calls configure)"""
    # Same logic as current _load_plugin but calls configure() instead of load_plugin()
    # ... (copy the existing logic)
    await plugin_instance.configure(self.server, plugin_instance.config)
    self.loaded_plugins[plugin_name] = plugin_instance
```

**Remove:** `async def load_plugins()` and `async def _load_plugin()`

### 3. **`faster_backend/nonix_web/server.py`**

**Change the constructor and lifespan methods:**

```python
class NxWebServer(FastAPI):
    def __init__(self, settings: Settings):
        super().__init__(
            title=settings.APP_NAME,
            debug=settings.DEBUG,
            lifespan=_lifespan
        )
        self.settings = settings
        self.plugin_manager = PluginManager(self, self.settings.PLUGIN_SEARCH_PATH)
        
        # STEP 1: Configure all plugins BEFORE lifespan starts
        await self.plugin_manager.configure_plugins(self.settings.PLUGINS)
        
        self.__init__server()

    async def _setup_server(self):
        # STEP 2: Startup all plugins DURING lifespan startup
        await self.plugin_manager.startup_plugins(self.settings.PLUGINS)

    async def _teardown_server(self):
        # STEP 3: Shutdown all plugins DURING lifespan shutdown
        await self.plugin_manager.shutdown_plugins()
```

### 4. **Plugin Files - Move Logic to Correct Methods**

#### **`faster_backend/nonix_web_cors/plugin.py`**
```python
class NxWebCORSPlugin(BasePlugin):
    async def configure(self, server: NxWebServer, config: Dict[str, Any]):
        # Move middleware here (BEFORE lifespan)
        server.add_middleware(
            CORSMiddleware,
            allow_origins=config.get("origins", _ALLOW_ALL),
            allow_credentials=config.get("allow_credentials", True),
            allow_methods=config.get("allow_methods", _ALLOW_ALL),
            allow_headers=config.get("allow_headers", _ALLOW_ALL),
        )
    
    # Remove _load_plugin method
```

#### **`faster_backend/nonix_web_db/plugin.py`**
```python
class NxWebDbPlugin(BasePlugin):
    async def startup(self, server: NxWebServer, config: Dict[str, Any]):
        # Move database creation here (DURING lifespan)
        global _async_session_local
        options = config.get("options", {})
        self.engine = engine = create_async_engine(config["url"], **options)
        set_async_session_local(async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False))
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def shutdown(self, server: NxWebServer):
        # Move cleanup here (DURING lifespan shutdown)
        if self.engine:
            await self.engine.dispose()
    
    # Remove _load_plugin method
```

#### **`faster_backend/nonix_web_static_files/plugin.py`**
```python
class NxWebStaticFilesPlugin(BasePlugin):
    async def configure(self, server: NxWebServer, config: Dict[str, Any]):
        # Move static mounting here (BEFORE lifespan)
        server.mount(
            config["path"],
            StaticFiles(
                directory=config["directory"],
                packages=config["packages"],
                html=config["html"],
                check_dir=config["check_dir"],
                follow_symlink=config["follow_symlink"],
            ),
            name=config["name"],
        )
    
    # Remove _load_plugin method
```

#### **`faster_backend/nonix_web_open_api/plugin.py`**
```python
class NxWebOpenApiPlugin(BasePlugin):
    async def configure(self, server: NxWebServer, config: Dict[str, Any]):
        # Move route registration here (BEFORE lifespan)
        openapi_route = config.get("openapi_route", "/openapi.json")
        docs_route = config.get("docs_route", "/docs")
        
        @server.get(openapi_route)
        async def openapi_spec(request: Request):
            # ... existing logic
        
        @server.get(docs_route)
        async def docs(tags: str = None):
            # ... existing logic
    
    # Remove _load_plugin method
```

#### **API Service Plugins** (file_manager, music_artist, agentic)
```python
class NxWebFileManagerPlugin(BasePlugin):
    api_services = [...]  # Keep existing
    
    async def configure(self, server: NxWebServer, config: Dict[str, Any]):
        # API services are handled automatically in BasePlugin.configure()
        await super().configure(server, config)
    
    # Remove _load_plugin method (it was empty anyway)
```

## Execution Order

1. **FastAPI instance created**
2. **`configure_plugins()` called** - middleware, routes, static files added
3. **Lifespan starts**
4. **`startup_plugins()` called** - database connections, async init
5. **Server starts accepting requests**
6. **Lifespan shutdown**
7. **`shutdown_plugins()` called** - cleanup, close connections

## Why This Fixes the Problem

- **Middleware gets added BEFORE** the lifespan starts
- **Database connections happen DURING** lifespan startup (when they should)
- **Cleanup happens DURING** lifespan shutdown (when it should)
- **No more "Cannot add middleware after app started"** errors

## Testing

After making these changes:
1. Start the server: `python main.py`
2. Check that CORS works (no middleware errors)
3. Check that database connects properly
4. Check that all API routes are available
5. Check that static files are served
