# Nonix LMStudio Plugin - Usage Guide

## Overview

The Nonix LMStudio Plugin provides seamless integration with LM Studio, enabling your application to leverage local Large Language Models (LLMs) through an OpenAI-compatible API. It automatically detects LM Studio installations, manages the LM Studio process lifecycle, and provides robust model management and text generation capabilities.

**⚠️ Important Philosophy**: This is a "hard plugin that comes after the app starts" - it depends on the daemon system for background process management and provides AI/LLM functionality as a service that other plugins can consume.

## Dependencies

### Required Systems
- **Plugin System**: For plugin registration and lifecycle management
- **Daemon System**: For background LM Studio process management (depends on "daemon" plugin)
- **DI System**: For service injection and dependency resolution

### Optional Dependencies
- **Web Framework Integration**: For exposing AI endpoints (if using web plugins)
- **Other AI Plugins**: Can consume LMStudio services

## Architecture

### Core Components
- **NxLMStudioPlugin**: Main plugin that orchestrates all components
- **LMStudioService**: High-level API service for other plugins to consume
- **LMStudioController**: Manages LM Studio process and API communication
- **LMStudioDaemon**: Background daemon that monitors LM Studio process health

### Data Flow
1. **Plugin loads** → Registers service and daemon with DI system
2. **Application starts** → Daemon manager starts LMStudio daemon
3. **Daemon starts** → Launches LM Studio process and monitors health
4. **Service exposes** → OpenAI-compatible API for text generation
5. **Other plugins inject** → Use LMStudio service for AI functionality

## Quick Start

### 1. Install LM Studio

First, install LM Studio on your system:
- **macOS**: Download from LM Studio website
- **Windows**: Download and install LM Studio
- **Linux**: Download AppImage or build from source

### 2. Configure the Plugin

Add the LMStudio plugin to your application:

```python
settings.PLUGINS = [
    {"name": "daemon"},        # Required: daemon system
    {"name": "lmstudio"},      # LMStudio plugin
    # ... other plugins
]
```

### 3. Use LMStudio Service

Inject the service in other plugins:

```python
import asyncio
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService
from nonix_plugin import BasePlugin

class AIPlugin(BasePlugin):
    lmstudio: LMStudioService = NxInject(LMStudioService)

    async def generate_text(self, prompt: str):
        return await self.lmstudio.generate_response(prompt)
```

That's it! The plugin will automatically:
- Detect your LM Studio installation
- Start the LM Studio process in the background
- Load available models
- Provide OpenAI-compatible API endpoints

## Configuration

### Basic Configuration

The plugin supports extensive configuration through `plugin.json`:

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
      "/Applications/LMStudio.app",
      "/usr/local/bin/lmstudio",
      "/opt/lmstudio",
      "~/LMStudio",
      "C:\\Program Files\\LM Studio",
      "C:\\Program Files (x86)\\LM Studio"
    ],
    "api_timeout": 30,
    "model_load_timeout": 60
  }
}
```

### Path Detection Priority

The plugin resolves LM Studio path in this order:

1. **Environment Variable**: `LMSTUDIO_PATH`
2. **Configuration**: `lmstudio_path` in config
3. **Auto-Detection**: Scans common installation locations
4. **Fallback Paths**: Tries predefined fallback locations

### Runtime Configuration

Override configuration when loading:

```python
plugins_to_load = [
    {
        "name": "lmstudio",
        "config": {
            "api_base_url": "http://localhost:8080",
            "auto_detect": false,
            "lmstudio_path": "/custom/path/to/lmstudio"
        }
    }
]
```

## Using LMStudio Service

### Text Generation

Generate text using loaded models:

```python
# Simple text generation
response = await lmstudio.generate_response("Hello, how are you?")

# Advanced generation with parameters
response = await lmstudio.generate_response(
    prompt="Write a short story about AI",
    max_tokens=500,
    temperature=0.8,
    top_p=0.9
)
```

### Chat Completion

Use chat-style conversations:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather like?"}
]

response = await lmstudio.chat_completion(messages)
```

### Model Management

Load and manage models:

```python
# Get available models
models = await lmstudio.get_available_models()
print(f"Available models: {[m['name'] for m in models]}")

# Load a specific model
success = await lmstudio.load_model("llama-2-7b-chat")

# Unload a model
success = await lmstudio.unload_model("llama-2-7b-chat")
```

### Server Status and Health

Monitor LM Studio health:

```python
# Get server status
status = await lmstudio.get_server_status()
print(f"Server ready: {status['service_ready']}")

# Health check
is_healthy = await lmstudio.health_check()

# Get service information
info = lmstudio.get_service_info()
```

## Process Management

### Automatic Lifecycle

The plugin automatically manages the LM Studio process:

- **Startup**: Launches LM Studio and waits for API readiness
- **Monitoring**: Continuously monitors process and API health
- **Recovery**: Automatically restarts LM Studio if it crashes
- **Shutdown**: Gracefully terminates LM Studio on application shutdown

### Manual Control

You can also control the LM Studio process manually:

```python
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

# Get LMStudio service instance
lmstudio: LMStudioService = NxInject(LMStudioService)

# Start LM Studio
success = await lmstudio.start_daemon()

# Stop LM Studio
success = await lmstudio.stop_daemon()

# Restart LM Studio
success = await lmstudio.restart_daemon()
```

## Error Handling

### Connection Issues

The plugin handles various connection scenarios:

```python
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

# Get LMStudio service instance
lmstudio: LMStudioService = NxInject(LMStudioService)

try:
    response = await lmstudio.generate_response("Test prompt")
    if response is None:
        print("LM Studio is not responding - check if it's running")
except Exception as e:
    print(f"Error communicating with LM Studio: {e}")
```

### Process Management Errors

Handle process-related errors:

```python
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

# Get LMStudio service instance
lmstudio: LMStudioService = NxInject(LMStudioService)

# Check if daemon is running
status = await lmstudio.get_server_status()
if not status.get("service_ready"):
    print("LM Studio daemon is not ready")

    # Try to restart
    success = await lmstudio.restart_daemon()
    if success:
        print("LM Studio restarted successfully")
```

### Model Loading Errors

Handle model-related errors:

```python
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

# Get LMStudio service instance
lmstudio: LMStudioService = NxInject(LMStudioService)

success = await lmstudio.load_model("nonexistent-model")
if not success:
    print("Failed to load model - check model name and availability")

# Always check available models first
models = await lmstudio.get_available_models()
available_names = [m['name'] for m in models]
```

## Advanced Usage Patterns

### Custom AI Service

Create a custom AI service that wraps LMStudio:

```python
import asyncio
from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService
from nonix_plugin import BasePlugin

class CustomAIService:
    def __init__(self):
        self.lmstudio = NxInject(LMStudioService)

    async def summarize_text(self, text: str, max_length: int = 100):
        prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}"
        return await self.lmstudio.generate_response(
            prompt,
            max_tokens=max_length * 2,
            temperature=0.3
        )

    async def classify_sentiment(self, text: str):
        prompt = f"Classify the sentiment of this text as positive, negative, or neutral:\n\n{text}"
        response = await self.lmstudio.generate_response(prompt, max_tokens=10)
        return response.strip().lower()

@injectables([CustomAIService])
class AIServicePlugin(BasePlugin):
    pass
```

### Background AI Processing

Use with daemon system for continuous AI tasks:

```python
import asyncio
from nonix_daemon import NxAsyncioDaemon, daemons
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService
from nonix_plugin import BasePlugin

class AIProcessingDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("ai-processor")
        self.lmstudio = NxInject(LMStudioService)

    async def _run(self):
        while True:
            try:
                # Process queued AI tasks
                await self.process_ai_queue()
                await asyncio.sleep(60)  # Process every minute
            except Exception as e:
                self.logger.error(f"AI processing error: {e}")
                await asyncio.sleep(30)

@daemons([AIProcessingDaemon])
class AIProcessingPlugin(BasePlugin):
    pass
```

### Multi-Model Management

Manage multiple models efficiently:

```python
import asyncio
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

class ModelManagerService:
    def __init__(self):
        self.lmstudio = NxInject(LMStudioService)
        self.loaded_models = set()

    async def ensure_model_loaded(self, model_name: str):
        if model_name not in self.loaded_models:
            success = await self.lmstudio.load_model(model_name)
            if success:
                self.loaded_models.add(model_name)
                return True
        return model_name in self.loaded_models

    async def generate_with_model(self, model_name: str, prompt: str):
        await self.ensure_model_loaded(model_name)
        return await self.lmstudio.generate_response(prompt, model=model_name)

    async def unload_unused_models(self):
        # Unload models that haven't been used recently
        available = await self.lmstudio.get_available_models()
        for model in available:
            if model['name'] not in self.loaded_models:
                await self.lmstudio.unload_model(model['name'])
```

## Integration Examples

### FastAPI Integration

Expose AI endpoints via web framework:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from nonix_di.resolve import di_resolve
from nonix_lmstudio.services.lmstudio_service import LMStudioService

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

@app.post("/api/generate")
async def generate_text(request: GenerateRequest):
    lmstudio = di_resolve(LMStudioService)
    if not lmstudio:
        raise HTTPException(status_code=503, detail="LM Studio not available")

    response = await lmstudio.generate_response(
        request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )

    if response is None:
        raise HTTPException(status_code=500, detail="Generation failed")

    return {"response": response}
```

### Queue-Based Processing

Integrate with background job queues:

```python
import asyncio
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

class AIJobProcessor:
    def __init__(self):
        self.lmstudio = NxInject(LMStudioService)
        self.job_queue = []  # Your job queue implementation

    async def process_job(self, job):
        job_type = job.get("type")

        if job_type == "text_generation":
            result = await self.lmstudio.generate_response(job["prompt"])
        elif job_type == "chat_completion":
            result = await self.lmstudio.chat_completion(job["messages"])
        elif job_type == "model_load":
            result = await self.lmstudio.load_model(job["model_name"])

        return result

    async def run_processor(self):
        while True:
            if self.job_queue:
                job = self.job_queue.pop(0)
                result = await self.process_job(job)
                # Handle result...
            await asyncio.sleep(1)
```

## Monitoring and Observability

### Health Monitoring

Monitor LM Studio health and performance:

```python
import asyncio
from datetime import datetime
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

class LMStudioMonitor:
    def __init__(self):
        self.lmstudio = NxInject(LMStudioService)

    async def get_health_metrics(self):
        status = await self.lmstudio.get_server_status()
        models = await self.lmstudio.get_available_models()

        return {
            "lmstudio_ready": status.get("service_ready", False),
            "api_url": status.get("controller", {}).get("api_base_url"),
            "models_loaded": len(models),
            "server_info": status.get("server", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def log_metrics(self):
        metrics = await self.get_health_metrics()
        self.logger.info(f"LMStudio Health: {metrics}")
```

### Performance Monitoring

Track generation performance:

```python
import time
from nonix_di.resolve import NxInject
from nonix_lmstudio.services.lmstudio_service import LMStudioService

class PerformanceMonitor:
    def __init__(self):
        self.lmstudio = NxInject(LMStudioService)
        self.generation_times = []
        self.error_count = 0

    async def time_generation(self, prompt: str):
        start_time = time.time()
        try:
            result = await self.lmstudio.generate_response(prompt)
            duration = time.time() - start_time

            self.generation_times.append(duration)
            return result, duration

        except Exception as e:
            self.error_count += 1
            raise e

    def get_stats(self):
        if not self.generation_times:
            return {"avg_time": 0, "total_generations": 0, "error_rate": 0}

        avg_time = sum(self.generation_times) / len(self.generation_times)
        total = len(self.generation_times)
        error_rate = self.error_count / (total + self.error_count)

        return {
            "avg_generation_time": avg_time,
            "total_generations": total,
            "error_rate": error_rate
        }
```

## Troubleshooting

### LM Studio Not Found

**Problem**: Plugin can't find LM Studio installation

**Solutions**:
```bash
# Set environment variable
export LMSTUDIO_PATH="/path/to/lmstudio"

# Or configure in plugin settings
"lmstudio_path": "/path/to/lmstudio"
```

### API Connection Failed

**Problem**: Can't connect to LM Studio API

**Solutions**:
- Check if LM Studio is running
- Verify API URL configuration
- Check firewall settings
- Ensure correct port (default: 1234)

### Model Loading Failed

**Problem**: Model fails to load

**Solutions**:
- Check model file exists and is valid
- Ensure sufficient RAM for model
- Check LM Studio logs for specific errors
- Try loading smaller models first

### Process Crashes

**Problem**: LM Studio process keeps crashing

**Solutions**:
- Check system resources (RAM, disk space)
- Update LM Studio to latest version
- Check LM Studio application logs
- Try different models or smaller models

## Best Practices

### 1. Resource Management

```python
# Always check health before using
if await lmstudio.health_check():
    response = await lmstudio.generate_response(prompt)
else:
    # Handle offline state
    pass
```

### 2. Error Handling

```python
# Implement retry logic for transient failures
async def generate_with_retry(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await lmstudio.generate_response(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return None
```

### 3. Model Management

```python
# Pre-load frequently used models
class ModelPreloader:
    async def preload_models(self):
        common_models = ["llama-2-7b-chat", "codellama-7b"]
        for model in common_models:
            success = await lmstudio.load_model(model)
            if success:
                print(f"Pre-loaded model: {model}")
```

### 4. Performance Optimization

```python
# Use appropriate parameters for different use cases
# Creative writing
creative = await lmstudio.generate_response(
    prompt, temperature=0.9, top_p=0.9, max_tokens=500
)

# Code generation
code = await lmstudio.generate_response(
    prompt, temperature=0.2, top_p=0.1, max_tokens=200
)

# Analysis/summarization
analysis = await lmstudio.generate_response(
    prompt, temperature=0.1, top_p=0.5, max_tokens=300
)
```

## Key Principles

### Plugin as AI Service Provider
- **LMStudio Plugin** = Loader that provides AI capabilities
- **LMStudio Service** = The actual AI functionality that gets injected
- **Integration** = Services by type, plugin by name when needed

### When to Use What
- **NxInject(LMStudioService)**: Most common - inject AI capabilities
- **NxInjectPlugin("lmstudio")**: Rare - only for plugin-specific operations
- **Direct service access**: Always prefer service injection

### The Flow
1. **Plugin loads** → Registers LMStudio service and daemon
2. **Daemon starts** → Launches and monitors LM Studio process
3. **Service exposes** → AI capabilities via OpenAI-compatible API
4. **Application injects** → Uses AI services for text generation and model management
5. **Background monitoring** → Ensures LM Studio stays healthy and responsive

**Remember**: The LMStudio plugin is a comprehensive AI service provider that leverages the daemon system for process management and the DI system for service distribution. It's designed as a "hard plugin that comes after the app starts" to provide robust local AI capabilities.

## Plugin Development Workflow

1. **Install LM Studio** - Set up LM Studio on your target platform
2. **Configure Plugin** - Add lmstudio plugin with proper settings
3. **Test Connection** - Verify plugin can detect and start LM Studio
4. **Load Models** - Test model loading and unloading functionality
5. **Integrate Services** - Use LMStudio service in your application logic
6. **Add Monitoring** - Implement health checks and error handling
7. **Optimize Performance** - Tune parameters for your specific use cases

The LMStudio plugin transforms your application into an AI-powered system by seamlessly integrating local language models through a familiar OpenAI-compatible interface, all managed automatically through the plugin architecture.
