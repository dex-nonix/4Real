# LM Studio Plugin

A comprehensive plugin for integrating LM Studio with the NxWebServer framework. Provides automatic path detection, background process management, and injectable controllers for AI operations.

## Features

- 🚀 **Automatic Path Detection**: Cross-platform detection of LM Studio installation
- 🔄 **Background Process Management**: Daemon-based LM Studio process monitoring and restart
- 💉 **Injectable Controller**: Full dependency injection support for controllers and services
- 🤖 **AI Operations**: Text generation, chat completion, and model management
- 🌐 **OpenAI-Compatible API**: Compatible with LM Studio's OpenAI-style API
- ⚙️ **Flexible Configuration**: Environment variables, config files, and auto-detection
- 🔍 **Health Monitoring**: API health checks and process monitoring

## Architecture

### Components

1. **LMStudioController**: Main control interface for LM Studio operations
2. **LMStudioService**: High-level service API for AI operations
3. **LMStudioDaemon**: Background process management and monitoring
4. **LMStudioPathDetector**: Cross-platform path detection utility

### Directory Structure

```
nonix_lmstudio/
├── plugin.json          # Plugin metadata and configuration
├── plugin.py           # Main plugin class
├── controllers/
│   ├── __init__.py
│   └── lmstudio_controller.py  # Main controller
├── services/
│   ├── __init__.py
│   └── lmstudio_service.py     # Service layer
├── daemons/
│   ├── __init__.py
│   └── lmstudio_daemon.py      # Background daemon
├── path_detector.py    # Path detection utility
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
from nonix_plugin.descriptor import NxInjectPlugin

class MyPlugin(BasePlugin):
    # Inject the LM Studio plugin
    lmstudio = NxInjectPlugin("lmstudio")

    async def _startup(self, config):
        # Start LM Studio
        await self.lmstudio.start_lmstudio()

        # Generate text
        response = await self.lmstudio.generate_text("Hello, how are you?")
        print(response)
```

### Advanced Usage

```python
from nonix_di.resolve import NxInject

class AdvancedPlugin(BasePlugin):
    # Inject LM Studio controller directly
    controller = NxInject(LMStudioController)
    service = NxInject(LMStudioService)

    async def complex_ai_operation(self):
        # Get available models
        models = await self.service.get_available_models()

        # Load a specific model
        await self.service.load_model("my-model-name")

        # Generate with custom parameters
        response = await self.service.generate_response(
            prompt="Explain quantum computing",
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

### LMStudioController

```python
class LMStudioController:
    async def start_lmstudio() -> bool
    async def stop_lmstudio() -> bool
    async def get_models() -> List[Dict[str, Any]]
    async def load_model(model_name: str) -> bool
    async def unload_model(model_name: str) -> bool
    async def generate_text(prompt: str, **kwargs) -> Optional[str]
    async def get_server_info() -> Optional[Dict[str, Any]]
    def get_status() -> Dict[str, Any]
```

### LMStudioService

```python
class LMStudioService:
    async def start_service() -> bool
    async def stop_service() -> bool
    async def get_available_models() -> List[Dict[str, Any]]
    async def load_model(model_name: str) -> bool
    async def unload_model(model_name: str) -> bool
    async def generate_response(prompt: str, **kwargs) -> Optional[str]
    async def chat_completion(messages: List[Dict], **kwargs) -> Optional[str]
    async def get_server_status() -> Dict[str, Any]
    async def health_check() -> bool
```

## Platform Support

### Windows
- Searches: `C:\Program Files\LM Studio\`, `AppData\Local\LM Studio\`
- Executable: `LM-Studio.exe`

### macOS
- Searches: `/Applications/LM Studio.app/`, user Applications
- Executable: `LM Studio` (inside app bundle)

### Linux
- Searches: `/usr/local/bin/`, `/opt/lmstudio/`, `~/.lmstudio/`
- Executable: `lmstudio`

## Dependencies

- `daemon` plugin (automatically managed)
- `aiohttp` for HTTP client operations
- LM Studio application installed and accessible

## Error Handling

The plugin includes comprehensive error handling:

- **Path Resolution**: Multiple fallback mechanisms for finding LM Studio
- **Process Management**: Automatic restart on unexpected termination
- **API Communication**: Timeout handling and retry logic
- **Health Monitoring**: Continuous API health checks

## Troubleshooting

### Common Issues

1. **LM Studio not found**:
   - Check `LMSTUDIO_PATH` environment variable
   - Verify LM Studio is installed in standard location
   - Update `fallback_paths` in config

2. **API connection failed**:
   - Ensure LM Studio is running on port 1234
   - Check firewall settings
   - Verify API timeout configuration

3. **Process won't start**:
   - Check file permissions on LM Studio executable
   - Verify path is correct for your platform
   - Check system logs for startup errors

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

- **0.1.0**: Initial release with full LM Studio integration
  - Cross-platform path detection
  - Background process management
  - Injectable controller architecture
  - OpenAI-compatible API
  - Comprehensive error handling
