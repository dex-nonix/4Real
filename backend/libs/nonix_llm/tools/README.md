# Nonix LLM Tools

A universal tool management system that supports multiple AI frameworks including LangChain, MCP (Model Context Protocol), and OpenAI function calling. Provides dynamic tool loading, runtime management, and seamless framework interoperability.

## Overview

The Nonix LLM Tools system provides:

- **Universal Tool References**: Support for multiple tool types and sources
- **Framework Adapters**: Convert between LangChain, MCP, and OpenAI formats
- **Dynamic Loading**: Hot reload support with change detection
- **Runtime Management**: Enable/disable tools on the fly
- **Unified API**: Single interface for all tool types

## Quick Start

```python
from nonix_llm.tools import NxLLMToolsManager

# Initialize with config
config = {
    "langchain_tools": [
        {"langchain_tool": my_langchain_tool}
    ],
    "mcp_clients": [
        {
            "mcp_client": {
                "command": "uvx",
                "args": ["mcp-server-git"],
                "env": {"GIT_REPO_PATH": "/path/to/repo"}
            }
        }
    ],
    "file_tools": [
        {"file": "path/to/tools.py"}
    ]
}

manager = NxLLMToolsManager(config)

# Get tools in different formats
langchain_tools = manager.get_langchain_tools()
mcp_tools = manager.get_mcp_tools()
openai_tools = manager.get_openai_tools()

# Runtime management
manager.disable_tool("tool_name")
manager.enable_tool("tool_name")
```

## Tool Reference Types

### 1. LangChain Tool Reference

Load LangChain Tool instances directly:

```python
from langchain.tools import Tool

my_tool = Tool(
    name="calculator",
    description="Performs calculations",
    func=lambda x: eval(x)
)

config = {
    "langchain_tools": [
        {"langchain_tool": my_tool},
        {"langchain_tool": my_tool, "disabled": True}  # Disabled tool
    ]
}
```

### 2. MCP Client Reference

Connect to MCP servers:

```python
config = {
    "mcp_clients": [
        {
            "mcp_client": {
                "command": "uvx",
                "args": ["mcp-server-filesystem"],
                "env": {"FILESYSTEM_ROOT": "/tmp"}
            }
        },
        {
            "mcp_client": existing_mcp_client_instance
        }
    ]
}
```

### 3. File Reference

Load tools from Python files:

```python
config = {
    "file_tools": [
        {"file": "my_tools.py"},
        {"file": "tools/advanced.py", "disabled": True}
    ]
}
```

### 4. Module Reference

Load from Python modules:

```python
config = {
    "module_tools": [
        {"module": "my_package.tools"},
        {"module:function": "utils.math:calculator"}
    ]
}
```

### 5. Object Reference

Load from object attributes:

```python
config = {
    "object_tools": [
        {"object": my_service, "attr": "tools"},
        {"object": "global_service", "attr": "get_tools"}
    ]
}
```

### 6. Folder Reference

Load all tools from a directory:

```python
config = {
    "folder_tools": [
        {"folder": "tools/"},
        {"folder": "plugins/", "pattern": "*.py"}
    ]
}
```

### 7. Config Dict Reference

Inline tool definitions:

```python
config = {
    "config_tools": [
        {
            "name": "weather",
            "description": "Get weather info",
            "function": "weather_service:get_weather"
        }
    ]
}
```

## Universal Disabled Flag

Any tool reference can be disabled using the `"disabled": True` flag:

```python
config = {
    "file_tools": [
        {"file": "tools.py", "disabled": True}
    ],
    "langchain_tools": [
        {"langchain_tool": my_tool, "disabled": False}
    ],
    "mcp_clients": [
        {"mcp_client": {...}, "disabled": True}
    ]
}
```

## Framework Adapters

### LangChain Integration

```python
# Get LangChain Tool instances
tools = manager.get_langchain_tools()

# Use with LangChain agents
from langchain.agents import initialize_agent
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description")
```

### MCP Integration

```python
# Get MCP-compatible format
mcp_tools = manager.get_mcp_tools()

# Use with MCP clients
for tool in mcp_tools:
    result = await mcp_client.call_tool(tool["name"], tool["arguments"])
```

### OpenAI Function Calling

```python
# Get OpenAI function schemas
functions = manager.get_openai_tools()

# Use with OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Help me"}],
    functions=functions
)
```

## Runtime Management

### Enable/Disable Tools

```python
# Disable a tool at runtime
manager.disable_tool("calculator")

# Enable a tool at runtime
manager.enable_tool("calculator")

# Check tool status
is_enabled = manager.is_tool_enabled("calculator")
```

### Reload Tools

```python
# Force reload all tools
manager.reload_all_tools()

# Reload specific reference
manager.reload_reference(reference_id)
```

## Tool Decorators

### @llm_tool Decorator

Mark functions as LangChain-compatible tools:

```python
from nonix_llm.tools.decorators import llm_tool

@llm_tool(
    name="calculator",
    description="Performs mathematical calculations"
)
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    return str(eval(expression))
```

### Custom Args Schema

```python
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate")

@llm_tool(
    name="calculator",
    description="Performs calculations",
    args_schema=CalculatorInput
)
def calculate(expression: str) -> str:
    return str(eval(expression))
```

## Advanced Features

### Context and Partials

Apply context and partial arguments to tools:

```python
manager = NxLLMToolsManager(
    config,
    context={"user_id": "123", "session": session},
    partials={"api_key": "secret"}
)
```

### Change Detection

Automatic reload when files change:

```python
# Enable change detection (default: True)
manager = NxLLMToolsManager(config, auto_reload=True)

# Tools automatically reload when source files change
```

### Error Handling

```python
try:
    tools = manager.get_langchain_tools()
except ToolLoadError as e:
    print(f"Failed to load tools: {e}")
except ToolValidationError as e:
    print(f"Tool validation failed: {e}")
```

## Integration with Other Nonix Components

### ChainChin Integration

```python
from nonix_chainchin import ChainChin

chain = ChainChin({
    "llm": {
        "tools": {
            "file_tools": [{"file": "tools.py"}],
            "mcp_clients": [{"mcp_client": {...}}]
        }
    }
})
```

### Media Transcriber Integration

```python
from nonix_media_transcriber import MediaTranscriber

transcriber = MediaTranscriber({
    "langchain_middleware": {
        "tools": {
            "langchain_tools": [{"langchain_tool": transcription_tool}]
        }
    }
})
```

## File Structure

```
tools/
├── __init__.py              # Main exports
├── README.md               # This file
├── tools_manager.py        # Main NxLLMToolsManager class
├── decorators.py           # @llm_tool decorator
├── file_tools.py           # File-based tool utilities
├── utils.py                # Utility functions
├── integration_verification.py  # Tool validation
└── tool_references/        # Tool reference implementations
    ├── __init__.py
    ├── base.py             # Base ToolReference class
    ├── file_reference.py   # File-based tools
    ├── module_reference.py # Module-based tools
    ├── object_reference.py # Object attribute tools
    ├── folder_reference.py # Directory scanning
    ├── config_dict_reference.py  # Inline definitions
    ├── lang_chain_reference.py   # LangChain tools
    ├── mcp_client_reference.py   # MCP integration
    └── nested_manager_reference.py  # Nested managers
```

## Best Practices

### Tool Organization

1. **Group Related Tools**: Use folders or modules for related functionality
2. **Clear Naming**: Use descriptive names and documentation
3. **Error Handling**: Implement proper error handling in tools
4. **Type Hints**: Use type hints for better IDE support

### Performance

1. **Lazy Loading**: Tools are loaded on-demand by default
2. **Caching**: Tool instances are cached and reused
3. **Change Detection**: Only reload when files actually change
4. **Async Support**: MCP tools support async operations

### Security

1. **Validation**: All tools are validated before loading
2. **Sandboxing**: Consider tool execution environment
3. **Access Control**: Use context to control tool access
4. **Input Validation**: Validate tool inputs with Pydantic schemas

## Migration Guide

### From Custom Tool Systems

1. **Identify Tool Types**: Determine what type of reference each tool needs
2. **Update Configuration**: Convert to new config format
3. **Test Framework Adapters**: Ensure tools work with target frameworks
4. **Enable Change Detection**: Set up automatic reloading

### From LangChain-Only

1. **Wrap Existing Tools**: Use `LangChainToolReference`
2. **Add MCP Clients**: Integrate external MCP servers
3. **Update Initialization**: Use `NxLLMToolsManager`
4. **Test Compatibility**: Verify tools work with adapters

## Troubleshooting

### Common Issues

1. **Import Errors**: Check module paths and dependencies
2. **Tool Not Found**: Verify file paths and function names
3. **Validation Failures**: Check Pydantic schemas and types
4. **MCP Connection**: Verify server commands and environment

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = NxLLMToolsManager(config, debug=True)
```

### Tool Inspection

```python
# List all loaded tools
for tool in manager.get_all_tools():
    print(f"Tool: {tool.name} - {tool.description}")

# Get tool metadata
metadata = manager.get_tool_metadata("tool_name")
print(f"Source: {metadata['source']}")
print(f"Type: {metadata['type']}")
```

## Contributing

1. **Add New Reference Types**: Extend `ToolReference` base class
2. **Framework Adapters**: Add support for new AI frameworks
3. **Tool Decorators**: Enhance decorator functionality
4. **Documentation**: Update README and docstrings
5. **Tests**: Add comprehensive test coverage

## License

Part of the Nonix framework - see main project license. 