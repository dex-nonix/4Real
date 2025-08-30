# Plugin UI System Architecture

## Overview

This document describes a comprehensive plugin system that allows plugins to deliver their own UI components, styles, and functionality to a Vue.js frontend application. The system supports dynamic loading, hot reloading, and compilation of various file formats on-demand.

## System Architecture

### Core Principles

1. **Two-Step Loading**: Discovery/Configuration → Runtime Loading
2. **On-Demand Compilation**: Files compiled when first requested
3. **Hot Reload**: WebSocket-based file change notifications
4. **Language Agnostic**: Support for Vue, SCSS, TypeScript, and more
5. **No Global State**: Clean parameter-based communication

### Backend Components

#### Plugin Manager
- Discovers available plugins
- Manages plugin lifecycle (configure, startup, shutdown)
- Handles dependency resolution
- Tracks plugin status

#### File Watcher
- Monitors plugin file changes
- Emits WebSocket notifications
- Implements debounced change detection

#### Compilation Service
- Compiles various file formats on-demand
- Caches compilation results
- Supports Vue SFC, SCSS, TypeScript, CSS processing

#### Static File Server
- Serves plugin UI files
- Mounts plugin directories dynamically
- Only available when plugin is loaded

### Frontend Components

#### Plugin Manager
- Loads and manages plugins
- Handles component registration
- Manages plugin lifecycle

#### Hot Reload Service
- Listens for WebSocket notifications
- Triggers plugin reloads
- Implements debounced reloading

#### Registry System
- Manages available widgets/components
- Supports dynamic registration
- Categorized by type (display, edit, dynamic, layout, page)

## Implementation Details

### Backend Implementation

#### Base Plugin Class
```python
class BasePlugin(ABC):
    api_services = []
    ui_static_path = None
    
    def _configure(self, server: "NxWebServer", config: Dict[str, Any]):
        # Register API services
        for routed_service in self.api_services:
            server.app.include_router(routed_service.to_router(), prefix="/api")
        
        # Register UI static files if plugin has them
        if self.ui_static_path:
            self._register_ui_static_files(server)
    
    def _register_ui_static_files(self, server: "NxWebServer"):
        """Register plugin's UI static files with the server"""
        if not self.ui_static_path:
            return
            
        plugin_ui_path = f"/plugins/{self.name}/ui"
        plugin_static_dir = self.ui_static_path
        
        # Mount plugin's UI static files
        server.app.mount(
            plugin_ui_path,
            StaticFiles(directory=plugin_static_dir),
            name=f"plugin-{self.name}-ui"
        )
```

#### Plugin Manager
```python
class PluginManager:
    def __init__(self, server: "NxWebServer", plugin_paths: Union[str, List[str]]):
        self.server = server
        self.plugin_paths = plugin_paths
        self.available_plugins = {}
        self.loaded_plugins = {}
        self.active_ui_mounts = {}
        
        # Initialize file watcher
        self.file_watcher = PluginFileWatcher(plugin_paths)
        self.file_watcher.start_watching()
    
    def _configure_plugin(self, plugin_name: str, plugin_data: Dict[str, Any], override_config: Dict[str, Any]):
        # ... existing configuration code ...
        
        plugin_instance = PluginClass(config=final_config)
        plugin_instance.name = plugin_name
        plugin_instance.version = metadata.get("version", "0.0.0")
        
        self.loaded_plugins[plugin_name] = plugin_instance
        
        # Configure plugin (this will register UI static files)
        plugin_instance.configure(self.server, plugin_instance.config)
        
        # Track UI mount if plugin has UI
        if hasattr(plugin_instance, 'ui_static_path') and plugin_instance.ui_static_path:
            self.active_ui_mounts[plugin_name] = {
                'path': f"/plugins/{plugin_name}/ui",
                'directory': plugin_instance.ui_static_path
            }
```

#### File Watcher
```python
class PluginFileWatcher:
    def __init__(self, plugin_dirs):
        self.observer = Observer()
        self.plugin_dirs = plugin_dirs
        self.debounce_timer = None
        
    def start_watching(self):
        for plugin_dir in self.plugin_dirs:
            self.observer.schedule(
                PluginFileHandler(self),
                plugin_dir,
                recursive=True
            )
        self.observer.start()
    
    def on_file_change(self, file_path):
        # Debounce file changes
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        self.debounce_timer = asyncio.create_task(
            self._debounced_emit(file_path)
        )
    
    async def _debounced_emit(self, file_path, delay=300):
        await asyncio.sleep(delay / 1000)
        
        # Emit WebSocket event
        await emit_plugin_change({
            'type': 'plugin_file_changed',
            'file_path': file_path,
            'plugin_name': self._extract_plugin_name(file_path)
        })

class PluginFileHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.vue', '.js', '.css', '.scss', '.ts')):
            self.watcher.on_file_change(event.src_path)
```

#### Compilation Service
```python
class PluginCompilationService:
    def __init__(self):
        self.compilation_cache = {}
        self.compilers = {
            'scss': self.compile_scss,
            'ts': self.compile_typescript,
            'vue': self.compile_vue,
            'css': self.process_css
        }
    
    async def compile_plugin(self, plugin_path: Path, force_recompile=False):
        """Compile entire plugin on first demand"""
        cache_key = str(plugin_path)
        
        if not force_recompile and cache_key in self.compilation_cache:
            return self.compilation_cache[cache_key]
        
        # Compile all files in plugin
        compiled = {
            'components': {},
            'styles': {},
            'scripts': {},
            'assets': {}
        }
        
        # Compile Vue components
        vue_files = list(plugin_path.glob('**/*.vue'))
        for vue_file in vue_files:
            component_name = vue_file.stem
            compiled['components'][component_name] = await self.compile_vue(vue_file)
        
        # Compile SCSS files
        scss_files = list(plugin_path.glob('**/*.scss'))
        for scss_file in scss_files:
            style_name = scss_file.stem
            compiled['styles'][style_name] = await self.compile_scss(scss_file)
        
        # Compile TypeScript files
        ts_files = list(plugin_path.glob('**/*.ts'))
        for ts_file in ts_files:
            script_name = ts_file.stem
            compiled['scripts'][script_name] = await self.compile_typescript(ts_file)
        
        # Cache compiled result
        self.compilation_cache[cache_key] = compiled
        return compiled
    
    async def compile_scss(self, scss_file: Path) -> str:
        """Compile SCSS to CSS with variables and mixins"""
        try:
            scss_content = scss_file.read_text()
            
            # Add global SCSS variables and mixins
            global_scss = self._get_global_scss_context()
            full_scss = f"{global_scss}\n{scss_content}"
            
            # Compile SCSS to CSS
            css = sass.compile(string=full_scss, include_paths=[str(scss_file.parent)])
            
            # PostCSS processing (autoprefixer, etc.)
            processed_css = await self.process_css(css)
            
            return processed_css
        except Exception as e:
            self._logger.error(f"Failed to compile SCSS {scss_file}: {e}")
            return f"/* SCSS compilation failed: {e} */"
    
    async def compile_typescript(self, ts_file: Path) -> str:
        """Compile TypeScript to JavaScript"""
        try:
            ts_content = ts_file.read_text()
            
            # TypeScript compilation options
            compiler_options = {
                'target': 'ES2020',
                'module': 'ESNext',
                'moduleResolution': 'node',
                'esModuleInterop': True,
                'allowSyntheticDefaultImports': True
            }
            
            # Compile TypeScript
            js_code = typescript.compile(ts_content, compiler_options)
            
            return js_code
        except Exception as e:
            self._logger.error(f"Failed to compile TypeScript {ts_file}: {e}")
            return f"// TypeScript compilation failed: {e}"
    
    async def compile_vue(self, vue_file: Path) -> dict:
        """Compile Vue SFC to render function"""
        try:
            vue_content = vue_file.read_text()
            
            # Parse Vue SFC
            sfc = VueCompiler.parse(vue_content)
            
            # Compile template
            if sfc.template:
                template_compiled = VueCompiler.compileTemplate(sfc.template)
            
            # Compile script
            if sfc.script:
                script_compiled = await self.compile_typescript(
                    Path('temp.ts'), 
                    content=sfc.script
                )
            
            # Compile styles
            styles_compiled = []
            for style in sfc.styles:
                if style.lang == 'scss':
                    style_css = await self.compile_scss(
                        Path('temp.scss'), 
                        content=style.content
                    )
                else:
                    style_css = style.content
                styles_compiled.append(style_css)
            
            return {
                'template': template_compiled,
                'script': script_compiled,
                'styles': styles_compiled
            }
        except Exception as e:
            self._logger.error(f"Failed to compile Vue {vue_file}: {e}")
            return {'error': f'Vue compilation failed: {e}'}
```

#### API Endpoints
```python
@app.get("/api/plugins/ui")
async def get_plugin_ui_manifests():
    """Get list of plugins with UI"""
    plugin_manager = get_plugin_manager()
    
    available_plugins = []
    for plugin_name, plugin_instance in plugin_manager.loaded_plugins.items():
        if hasattr(plugin_instance, 'ui_static_path') and plugin_instance.ui_static_path:
            available_plugins.append({
                "name": plugin_name,
                "version": plugin_instance.version,
                "ui_url": f"/plugins/{plugin_name}/ui/index.js"
            })
    
    return available_plugins

@app.get("/api/plugins/{plugin_name}/compiled")
async def get_compiled_plugin(plugin_name: str):
    """Get compiled plugin files"""
    plugin_manager = get_plugin_manager()
    compilation_service = get_compilation_service()
    
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(404, f"Plugin {plugin_name} not found")
    
    # Compile plugin on first demand
    compiled = await compilation_service.compile_plugin(plugin.ui_static_path)
    return compiled
```

### Frontend Implementation

#### Plugin Manager
```javascript
class PluginManager {
  constructor(managers) {
    this.managers = managers
    this.loadedPlugins = new Map()
    this.compilationCache = new Map()
  }
  
  async loadPlugin(pluginName) {
    // Get plugin info
    const response = await fetch('/api/plugins/ui')
    const plugins = await response.json()
    
    const plugin = plugins.find(p => p.name === pluginName)
    if (!plugin) return
    
    // Load compiled plugin (backend handles compilation)
    const compiledPlugin = await this.loadCompiledPlugin(plugin)
    
    // Execute plugin
    const loadPlugin = compiledPlugin.default
    const unload = loadPlugin(this.managers, plugin.config || {})
    
    this.loadedPlugins.set(pluginName, { unload, plugin })
  }
  
  async loadCompiledPlugin(plugin) {
    // Backend compiles on first demand
    const response = await fetch(`/api/plugins/${plugin.name}/compiled`)
    const compiledPlugin = await response.json()
    
    // Create module from compiled code
    return this.createModuleFromCompiled(compiledPlugin)
  }
  
  createModuleFromCompiled(compiled) {
    // Create Vue components from compiled code
    const components = {}
    
    Object.entries(compiled.components).forEach(([name, componentData]) => {
      components[name] = this.createVueComponent(componentData)
    })
    
    // Create module that registers components
    return {
      default: function(managers, config) {
        Object.entries(components).forEach(([name, component]) => {
          managers.display.registerWidget(name, component, {})
        })
      }
    }
  }
  
  createVueComponent(componentData) {
    // Create Vue component from compiled template, script, styles
    return {
      name: componentData.name,
      template: componentData.template,
      setup: componentData.script,
      // Inject compiled styles
      mounted() {
        this.injectStyles(componentData.styles)
      },
      methods: {
        injectStyles(styles) {
          styles.forEach(style => {
            const styleElement = document.createElement('style')
            styleElement.textContent = style
            document.head.appendChild(styleElement)
          })
        }
      }
    }
  }
}
```

#### Hot Reload Service
```javascript
class PluginHotReloadService {
  constructor(websocketManager, pluginManager) {
    this.websocketManager = websocketManager
    this.pluginManager = pluginManager
    this.reloadQueue = new Map()
    
    this.setupWebSocketListeners()
  }
  
  setupWebSocketListeners() {
    this.websocketManager.on('plugin_file_changed', (data) => {
      this.handleFileChange(data)
    })
  }
  
  handleFileChange(data) {
    const { plugin_name, file_path } = data
    
    // Debounce reloads per plugin
    if (this.reloadQueue.has(plugin_name)) {
      clearTimeout(this.reloadQueue.get(plugin_name))
    }
    
    const reloadTimer = setTimeout(() => {
      this.reloadPlugin(plugin_name)
    }, 500) // 500ms debounce
    
    this.reloadQueue.set(plugin_name, reloadTimer)
  }
  
  async reloadPlugin(pluginName) {
    console.log(`Hot reloading plugin: ${pluginName}`)
    
    // Unload current plugin
    await this.pluginManager.unloadPlugin(pluginName)
    
    // Reload plugin (this will recompile .vue files)
    await this.pluginManager.loadPlugin(pluginName)
    
    console.log(`Plugin ${pluginName} hot reloaded successfully`)
  }
}
```

#### Bootstrap Integration
```javascript
// In bootstrap.js
const pluginManager = new FrontendPluginManager({
  display: DisplayWidgetManager,
  edit: EditWidgetManager,
  dynamic: DynamicWidgetManager,
  layout: LayoutManager,
  page: PageManager
})

// Make plugin manager available to app
app.provide('plugin-manager', pluginManager)

// Initialize hot reload service
const hotReloadService = new PluginHotReloadService(
  app.websocketManager, 
  pluginManager
)
```

## Plugin Development

### Plugin Structure
```
nonix_web_music_artist/
├── plugin.py                  # Plugin class
├── plugin.json               # Plugin metadata
├── ui/                       # UI files (mounted at /plugins/music-artist/ui/)
│   ├── index.js              # Main entry point
│   ├── components/           # Vue components
│   │   ├── ArtistCard.vue    # Vue SFC
│   │   └── ArtistForm.vue    # Vue SFC
│   ├── styles/               # Style files
│   │   ├── main.scss         # SCSS with variables
│   │   └── components.scss   # Component styles
│   ├── scripts/              # Script files
│   │   ├── utils.ts          # TypeScript utilities
│   │   └── services.ts       # TypeScript services
│   └── assets/               # Images, icons, etc.
```

### Plugin Entry Point (ui/index.js)
```javascript
// Plugin receives managers as parameters - no globals!
export default function loadMusicArtistPlugin(managers, config) {
  // managers = { display, edit, dynamic, layout, page }
  // config = plugin configuration
  
  // Register widgets with passed managers
  managers.display.registerWidget('artist-card', ArtistCard, {})
  managers.edit.registerWidget('artist-form', ArtistForm, {})
  managers.dynamic.registerWidget('artist-dashboard', ArtistDashboard, {})
  
  // Return cleanup function
  return function unload() {
    // Cleanup when plugin is unloaded
  }
}
```

### Plugin Class (plugin.py)
```python
class NxWebMusicArtistPlugin(BasePlugin):
    ui_static_path = "ui"  # This gets mounted at /plugins/music-artist/ui/
    
    api_services = [
        ArtistService,
        AlbumService,
        TrackService,
        StyleService,
        RhymeTechniqueService,
    ]
```

### Plugin Metadata (plugin.json)
```json
{
  "name": "music-artist",
  "version": "0.5.0",
  "class": "NxWebMusicArtistPlugin",
  "dependencies": ["db"],
  "config": {}
}
```

## Usage Examples

### Loading a Plugin
```javascript
// In any component or service
const pluginManager = inject('plugin-manager')

// Load plugin - it gets managers injected
await pluginManager.loadPlugin('music-artist')
```

### Plugin Development Workflow
1. **Create plugin structure** with `.vue`, `.scss`, `.ts` files
2. **Save files** → triggers backend compilation
3. **Backend compiles** all plugin files
4. **WebSocket notification** sent to browser
5. **Browser hot reloads** compiled plugin
6. **Everything works** with full language support

## Benefits

1. **Full Language Support**: SCSS, TypeScript, Vue SFC, etc.
2. **Compile on First Demand**: No precompilation needed
3. **Production Ready**: Optimized, minified output
4. **Hot Reload**: Recompiles on file changes
5. **Flexible**: Easy to add new compilers
6. **Cached**: Compiled results cached for performance
7. **No Build Tools**: Everything runs in backend
8. **Clean Architecture**: No global state, parameter-based communication
9. **Dynamic Loading**: Plugins loaded on-demand
10. **Isolated**: Each plugin manages its own resources

## Dependencies

### Backend
- `watchdog` - File system monitoring
- `sass` - SCSS compilation
- `typescript` - TypeScript compilation
- `vue-compiler` - Vue SFC compilation
- `postcss` - CSS processing

### Frontend
- Vue 3 with Composition API
- WebSocket support
- Dynamic import support

## Security Considerations

1. **Plugin Isolation**: Plugins run in isolated contexts
2. **File Access**: Only plugin-specific files accessible
3. **Compilation Safety**: Compilation errors don't crash system
4. **Resource Limits**: Implement compilation timeouts and memory limits
5. **Authentication**: Plugin loading can require authentication

## Performance Considerations

1. **Compilation Caching**: Compiled results cached to avoid recompilation
2. **Debounced Reloads**: File changes debounced to prevent excessive reloads
3. **Lazy Loading**: Plugins loaded only when needed
4. **Asset Optimization**: Images and assets optimized during compilation
5. **Memory Management**: Unused plugins properly cleaned up
