# LM Studio Plugin

A plugin for LM Studio integration with the NxWebServer framework. Handles lifecycle management of services and daemons through proper setup and teardown.

## Features

- 🔄 **Daemon Control**: Service-level methods to start/stop/restart LM Studio daemon
- 🔄 **Background Process Management**: Daemon-based LM Studio process monitoring
- 💉 **Service Injection**: LMStudioService available for injection with internal controller
- 🤖 **AI Operations**: Text generation, chat completion, and model management
- 🌐 **OpenAI-Compatible API**: Compatible with LM Studio's OpenAI-style API
- ⚙️ **Path Resolution**: Environment variable → config → fallback paths priority
- 🔍 **Health Monitoring**: API health checks and process status

## Architecture

### Components

1. **NxLMStudioPlugin**: Plugin with lifecycle management and service coordination
2. **LMStudioService**: Injectable service with internal controller and daemon control methods
3. **LMStudioController**: Internal control interface (not injectable)
4. **LMStudioDaemon**: Background process management and monitoring

### Directory Structure

```
nonix_lmstudio/
├── plugin.json          # Plugin metadata and configuration
├── plugin.py           # Plugin class with lifecycle management
├── controllers/
│   ├── __init__.py
│   └── lmstudio_controller.py  # Main controller
├── services/
│   ├── __init__.py
│   └── lmstudio_service.py     # Service layer with daemon control
├── daemons/
│   ├── __init__.py
│   └── lmstudio_daemon.py      # Background daemon
└── README.md          # This file
```

## Configuration

### Plugin Configuration

Add to your `main.py` settings:

```python
settings.PLUGINS = [
    # ... other plugins
    {"name": "lmstudio"},
    # ... other plugins
]
```

### Environment Variables

```bash
# Direct path to LM Studio executable
LMSTUDIO_PATH="/path/to/lm-studio"

# Or let the plugin auto-detect
# The plugin will search common installation locations
```

### Plugin Config (plugin.json)

```json
{
    "name": "lmstudio",
    "version": "0.1.0",
    "class": "NxLMStudioPlugin",
    "dependencies": ["daemon"],
    "config": {
        "lmstudio_path": null,
        "api_base_url": "http://localhost:1234",
        "auto_detect": true,
        "fallback_paths": [
            "/Applications/LM Studio.app",
            "/usr/local/bin/lmstudio"
        ],
        "api_timeout": 30,
        "model_load_timeout": 60
    }
}
```

## Usage

### Basic Usage

```python
from nonix_di.resolve import NxInject

class MyComponent:
    # Inject LM Studio service
    lmstudio = NxInject(LMStudioService)

    async def use_lm_studio(self):
        # Initialize service
        await self.lmstudio.initialize({
            "lmstudio_path": "/path/to/lm-studio",
            "api_base_url": "http://localhost:1234"
        })

        # Start LM Studio daemon
        await self.lmstudio.start_daemon()

        # Generate text
        response = await self.lmstudio.generate_response("Hello, how are you?")
        return response
```

### Plugin Injection (Advanced)

```python
from nonix_plugin.descriptor import NxInjectPlugin

class MyPlugin(BasePlugin):
    # Inject the LM Studio plugin itself (rarely needed)
    lmstudio_plugin = NxInjectPlugin("lmstudio")

    # Then inject the services you need
    lmstudio_service = NxInject(LMStudioService)

    async def _startup(self, config):
        # Use the injected service, not plugin methods
        await self.lmstudio_service.initialize(config)
        await self.lmstudio_service.start_daemon()
```

### Advanced Usage

```python
from nonix_di.resolve import NxInject

class AdvancedComponent:
    # Inject only the service (controller is internal)
    service = NxInject(LMStudioService)

    async def complex_operations(self):
        # Initialize service (this initializes the internal controller)
        await self.service.initialize({
            "lmstudio_path": "/path/to/lm-studio"
        })

        # Service daemon control
        await self.service.start_daemon()
        await self.service.restart_daemon()

        # Model operations
        models = await self.service.get_available_models()
        await self.service.load_model("my-model")

        # Text generation
        response = await self.service.generate_response(
            prompt="Explain AI",
            temperature=0.7,
            max_tokens=200
        )

        return response
```

### Chat Completion

```python
async def chat_example():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]

    response = await self.service.chat_completion(
        messages=messages,
        temperature=0.7
    )
```

## API Reference

### LMStudioController (Internal - Not Injectable)

```python
class LMStudioController:
    # Internal controller - created by service, not injected
    async def initialize(config: Dict[str, Any])
    async def start_lmstudio() -> bool
    async def stop_lmstudio() -> bool
    async def get_models() -> List[Dict[str, Any]]
    async def load_model(model_name: str) -> bool
    async def unload_model(model_name: str) -> bool
    async def generate_text(prompt: str, model: str = None, **kwargs) -> Optional[str]
    async def get_server_info() -> Optional[Dict[str, Any]]
    def get_status() -> Dict[str, Any]
    async def cleanup()
```

### LMStudioService

```python
class LMStudioService:
    async def initialize(config: Dict[str, Any])
    async def start_daemon() -> bool
    async def stop_daemon() -> bool
    async def restart_daemon() -> bool
    async def get_available_models() -> List[Dict[str, Any]]
    async def load_model(model_name: str) -> bool
    async def unload_model(model_name: str) -> bool
    async def generate_response(prompt: str, model: str = None, **kwargs) -> Optional[str]
    async def chat_completion(messages: List[Dict[str, str]], model: str = None, **kwargs) -> Optional[str]
    async def get_server_status() -> Dict[str, Any]
    async def health_check() -> bool
    def get_service_info() -> Dict[str, Any]
```

### NxLMStudioPlugin

```python
class NxLMStudioPlugin(BasePlugin):
    service: LMStudioService = NxInject(LMStudioService)

    async def _configure(config: Dict[str, Any])
    async def _startup(config: Dict[str, Any])
    async def _shutdown(config: Dict[str, Any])
```

## Configuration Paths

The plugin uses explicit fallback paths defined in `plugin.json`:

```json
"fallback_paths": [
    "/Applications/LM Studio.app/Contents/MacOS/LM Studio",
    "/Applications/LMStudio.app/Contents/MacOS/LMStudio",
    "/usr/local/bin/lmstudio",
    "/opt/lmstudio/bin/lmstudio",
    "~/LMStudio/lmstudio",
    "C:\\Program Files\\LM Studio\\LM-Studio.exe",
    "C:\\Program Files (x86)\\LM Studio\\LM-Studio.exe"
]
```

### Priority Order
1. `LMSTUDIO_PATH` environment variable
2. `lmstudio_path` in plugin config
3. Fallback paths (if `auto_detect: true`)
4. Error if no valid path found

## Dependencies

- `daemon` plugin (automatically managed)
- `aiohttp` for HTTP client operations
- LM Studio application installed and accessible

## Error Handling

The plugin includes robust error handling:

- **Path Validation**: Explicit path checking with clear error messages
- **Process Management**: Daemon handles process lifecycle and error recovery
- **API Communication**: Timeout handling and connection error management
- **Configuration**: Clear error messages for invalid configurations

## Troubleshooting

### Common Issues

1. **LM Studio path not found**:
   - Set `LMSTUDIO_PATH` environment variable to executable path
   - Or set `lmstudio_path` in plugin config
   - Or ensure `auto_detect: true` and valid `fallback_paths`

2. **Path validation errors**:
   - Ensure path exists and is executable (`chmod +x`)
   - Use absolute paths, not relative
   - Check file permissions

3. **Daemon startup failed**:
   - Verify LM Studio executable is valid
   - Check system has permissions to start processes
   - Review error logs from daemon initialization

4. **API connection failed**:
   - Ensure daemon started successfully first
   - Check LM Studio is responding on configured port
   - Verify API timeout settings

### Debug Mode

Enable debug logging to see detailed operation logs:

```python
settings.LOG_LEVEL = "debug"
```

## Examples

See the plugin code for comprehensive examples of:

- Controller injection and usage
- Service layer operations
- Daemon management
- Path detection
- Error handling patterns

## Version History

- **0.1.0**: LM Studio plugin with proper lifecycle management
  - Injectable service via decorators
  - Daemon-based process management
  - Service-level daemon control methods (`start_daemon`, `stop_daemon`, `restart_daemon`)
  - Plugin lifecycle management (_configure, _startup, _shutdown)
  - Service initialization and controller cleanup
  - Config-based path resolution with fallback paths
  - OpenAI-compatible API integration
  - Health monitoring and error handling
