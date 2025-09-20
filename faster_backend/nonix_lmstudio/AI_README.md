# AI_README: Nonix LMStudio API

## Requirements
- Python 3.8+
- nonix_plugin
- nonix_di
- nonix_daemon
- aiohttp

## Core Classes & Interfaces

### Main Plugin
```python
class NxLMStudioPlugin(BasePlugin):
    """LM Studio plugin for AI text generation"""
    def __init__(self, config: Dict[str, Any]) -> None
    async def _configure(self, config: Dict[str, Any]) -> None: """Initialize service with config"""
    async def _startup(self, config: Dict[str, Any]) -> None: """Plugin startup complete"""
    async def _shutdown(self, config: Dict[str, Any]) -> None: """Clean up service resources"""
    # Public attributes
    service: LMStudioService
```

### Service Layer
```python
class LMStudioService:
    """High-level API service for LM Studio operations"""
    def __init__(self) -> None
    async def initialize(self, config: Dict[str, Any]) -> None: """Initialize service with configuration"""
    async def start_daemon(self) -> bool: """Start LM Studio daemon process"""
    async def stop_daemon(self) -> bool: """Stop LM Studio daemon process"""
    async def restart_daemon(self) -> bool: """Restart LM Studio daemon process"""
    async def get_available_models(self) -> List[Dict[str, Any]]: """Get list of available models"""
    async def load_model(self, model_name: str) -> bool: """Load a specific model"""
    async def unload_model(self, model_name: str) -> bool: """Unload a specific model"""
    async def generate_response(self, prompt: str, model: str = None, **kwargs) -> Optional[str]: """Generate AI response"""
    async def chat_completion(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Optional[str]: """Chat completion with message history"""
    async def get_server_status(self) -> Dict[str, Any]: """Get LM Studio server status"""
    async def health_check(self) -> bool: """Check if service is healthy"""
    def get_service_info(self) -> Dict[str, Any]: """Get service information"""
    # Public attributes
    controller: LMStudioController
```

### Controller
```python
class LMStudioController:
    """Main controller for LM Studio operations"""
    def __init__(self) -> None
    async def initialize(self, config: Dict[str, Any]) -> None: """Initialize controller with config"""
    async def start_lmstudio(self) -> bool: """Start LM Studio through daemon"""
    async def stop_lmstudio(self) -> bool: """Stop LM Studio through daemon"""
    async def restart_lmstudio(self) -> bool: """Restart LM Studio through daemon"""
    async def get_models(self) -> List[Dict[str, Any]]: """Get available models from API"""
    async def load_model(self, model_name: str) -> bool: """Load model via API"""
    async def unload_model(self, model_name: str) -> bool: """Unload model via API"""
    async def generate_text(self, prompt: str, model: str = None, **kwargs) -> Optional[str]: """Generate text via API"""
    async def get_server_info(self) -> Dict[str, Any]: """Get server information"""
    def get_status(self) -> Dict[str, Any]: """Get controller status"""
    async def cleanup(self) -> None: """Clean up resources"""
    # Public attributes
    lmstudio_path: Optional[str]
    api_base_url: str
    session: Optional[aiohttp.ClientSession]
    models: List[Dict[str, Any]]
    is_running: bool
    api_timeout: int
    daemon_manager: NxDaemonManager
```

### Daemon
```python
class LMStudioDaemon(NxAsyncioDaemon):
    """Daemon for managing LM Studio background process"""
    def __init__(self, lmstudio_path: str, config: Dict[str, Any]) -> None
    async def _run(self) -> None: """Monitor LM Studio process and API health"""
    async def _start(self) -> None: """Start LM Studio process"""
    async def _stop(self) -> None: """Stop LM Studio process"""
    async def _restart_process(self) -> None: """Restart LM Studio after failure"""
    async def _wait_for_api_ready(self) -> None: """Wait for API to be available"""
    async def _check_api_health(self) -> None: """Check API health"""
    def get_process_info(self) -> Dict[str, Any]: """Get process information"""
    # Public attributes
    lmstudio_path: str
    config: Dict[str, Any]
    process: Optional[subprocess.Popen]
    api_base_url: str
    api_timeout: int
    is_process_running: bool
```

## Integration Points
```python
# Inject service in other plugins
from nonix_di import NxInject

class MyAIPlugin(BasePlugin):
    lmstudio: LMStudioService = NxInject(LMStudioService)

    async def generate_text(self, prompt: str) -> str:
        return await self.lmstudio.generate_response(prompt)

# Enable LM Studio plugin
settings.PLUGINS = [
    {"name": "daemon"},     # Required for daemon system
    {"name": "lmstudio"}    # LM Studio plugin
]

# Service usage examples
models = await lmstudio.get_available_models()
await lmstudio.load_model("model-name")
response = await lmstudio.generate_response("Hello, world!")
chat_response = await lmstudio.chat_completion([
    {"role": "user", "content": "Hello"}
])
status = await lmstudio.health_check()
```

## Configuration Schema
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
    "api_timeout": 30,
    "fallback_paths": [
      "/Applications/LM Studio.app",
      "/Applications/LMStudio.app",
      "/usr/local/bin/lmstudio",
      "/opt/lmstudio",
      "~/LMStudio"
    ]
  }
}
```
