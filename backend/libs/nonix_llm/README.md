# Nonix LLM Tools

A standalone module for managing LLM tools with security features and flexible configuration.

## Features

- **Tool Registration**: Register functions as LLM tools with flexible configuration
- **Hidden Properties**: Hide sensitive parameters from the LLM while making them available to functions
- **Path Safety**: Built-in utilities to prevent path traversal attacks
- **Parameter Descriptions**: Provide better documentation for tool parameters
- **Config-Based Loading**: Load tools from nested JSON configuration files

```python
from nonix_llm import llm_tool
from nonix_llm.tools.tools_manager import NxLLMToolsManager


# Using the decorator
@llm_tool(
    description="Read file contents securely",
    props={"root_path": "/safe/directory"},
    hidden_props=["root_path", "bind_root"],
    param_descriptions={"file_path": "Path to the file you want to read"}
)
def read_file(file_path: str, root_path=None, bind_root=True) -> str:
    """Read file contents with path safety."""
    from nonix_llm.tools.utils import resolve_safe_path

    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            bind_root=bind_root,
            must_exist=True
        )

        with open(safe_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


# Loading tools from configuration
tools_config = [
    {
        "func": "my_module:process_text",
        "name": "text_processor",
        "description": "Processes text content"
    },
    {
        "func": "file_tools:read_file",
        "props": {"root_path": "/safe/directory"},
        "hidden_props": ["root_path"]
    }
]

# Create a tools manager
tools_manager = NxLLMToolsManager()

# Register tools from config
tools = tools_manager.load_tools_from_config(tools_config)

# Use with your LLM framework
# ...
```

## Tool Configuration

Tools can be configured with the following options:

```python
@llm_tool(
    description="Tool description for the LLM",
    partial=["context", "config"],  # Bind runtime objects
    props={"default_param": "value"},  # Default parameters
    hidden_props=["api_key", "root_path"],  # Parameters hidden from LLM
    param_descriptions={  # Better parameter documentation
        "file_path": "Path to the file (relative to root)",
        "format": "Output format (json, text, markdown)"
    }
)
def my_tool(context, config, file_path, format="text", api_key=None, root_path=None):
    """Tool implementation."""
    # Implementation here
    pass
```

## Config-Based Tool Loading

Load tools from configuration dictionaries:

```python
tools_config = [
    # Simple function import
    {
        "func": "math:sqrt"
    },
    
    # Custom name and description
    {
        "func": "my_utils:process_text",
        "name": "text_processor",
        "description": "Processes and formats text content"
    },
    
    # With context binding
    {
        "func": "my_utils:save_to_output_dir",
        "partial": ["context"]
    },
    
    # With predefined properties
    {
        "func": "my_utils:format_text",
        "props": {
            "format": "markdown",
            "wrap_width": 80
        }
    },
    
    # With hidden properties
    {
        "func": "file_tools:read_file",
        "props": {
            "root_path": "/safe/directory",
            "bind_root": True
        },
        "hidden_props": ["root_path", "bind_root"]
    },
    
    # With parameter descriptions
    {
        "func": "file_tools:find_files",
        "description": "Find files matching a pattern",
        "param_descriptions": {
            "pattern": "Glob pattern to match files (e.g., '*.txt')",
            "directory": "Directory to search in (defaults to current directory)",
            "recursive": "Whether to search subdirectories recursively"
        }
    }
]

# Create a tools manager and load tools
tools_manager = NxLLMToolsManager()
tools = tools_manager.load_tools_from_config(tools_config)
```

## Path Safety Utilities

The `resolve_safe_path` utility function provides comprehensive path safety:

```python
from nonix_llm.tools.utils import resolve_safe_path

# Basic usage
safe_path = resolve_safe_path(
    path="user_input.txt",
    root_path="/safe/directory",
    bind_root=True
)

# With context
safe_path = resolve_safe_path(
    path="user_input.txt",
    context=context,
    context_key="output_dir",
    bind_root=True
)

# With directory creation
safe_path = resolve_safe_path(
    path="subdirectory/user_input.txt",
    root_path="/safe/directory",
    bind_root=True,
    create_dirs=True
)

# With existence check
safe_path = resolve_safe_path(
    path="user_input.txt",
    root_path="/safe/directory",
    bind_root=True,
    must_exist=True  # Will raise FileNotFoundError if file doesn't exist
)
```

### Path Safety Options

- **root_path**: Base directory to restrict operations to
- **context_key**: Key to extract root path from context
- **bind_root**: Whether to enforce path is within root directory
- **create_dirs**: Whether to create parent directories if they don't exist
- **must_exist**: Whether to verify the final path exists

## Integration with LangChain (Example)

Here's a dummy example showing how to integrate with LangChain:

```python
from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from nonix_llm.tools.tools_manager import NxLLMToolsManager

# Create a tools manager
tools_manager = NxLLMToolsManager()

# Load tools from config file
tools_config = [
    {
        "func": "file_tools:read_file",
        "props": {"root_path": "/safe/directory"},
        "hidden_props": ["root_path", "bind_root"]
    },
    {
        "func": "file_tools:write_file",
        "props": {"root_path": "/safe/directory"},
        "hidden_props": ["root_path", "bind_root"]
    }
]

# Load the tools
nonix_tools = tools_manager.load_tools_from_config(tools_config)

# Convert to LangChain tools
langchain_tools = []
for tool in nonix_tools:
    langchain_tools.append(
        Tool(
            name=tool["name"],
            description=tool["description"],
            func=tool["function"]
        )
    )

# Create LangChain agent
llm = ChatOpenAI(model="gpt-4")
prompt = PromptTemplate.from_template(
    """You are an assistant with access to the following tools:
    {tools}
    
    Use these tools to help the human.
    
    Human: {input}
    Assistant: """
)

agent = create_react_agent(llm, langchain_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True)

# Run the agent
response = agent_executor.invoke({"input": "Please read the file 'example.txt' and summarize its contents"})
print(response["output"])
```

## Using Tools from Class Instances

You can extract tools from class instances with decorated methods:

```python
from nonix_llm import llm_tool
from nonix_llm.tools.tools_manager import NxLLMToolsManager


class MyToolProvider:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    @llm_tool(
        description="Search for information",
        hidden_props=["api_key"],
        param_descriptions={"query": "Search query"}
    )
    def search(self, query: str, api_key=None) -> dict:
        """Search for information using the API."""
        # api_key is hidden from the LLM but available to the function
        api_key = api_key or self.api_key
        # Implementation using self.base_url and api_key
        return {"results": [f"Result for {query}"]}

    @llm_tool(
        description="Get recent items",
        param_descriptions={"count": "Number of items to return"}
    )
    def get_recent(self, count: int = 5) -> list:
        """Get recent items."""
        return [f"Item {i}" for i in range(count)]


# Create an instance
tool_provider = MyToolProvider(api_key="secret_key", base_url="https://api.example.com")

# Extract tools from the instance
tools_manager = NxLLMToolsManager()
tools = tools_manager.load_tools_from_instance(tool_provider)

# Now you can use these tools with your LLM framework
print(f"Loaded {len(tools)} tools from instance")
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")
```

## Loading Tools from Multiple Sources

You can load tools from various sources in one operation:

```python
from nonix_llm import llm_tool
from nonix_llm.tools.tools_manager import NxLLMToolsManager
import nonix_llm.tools.file_tools as file_tools

# Create a tools manager
tools_manager = NxLLMToolsManager()


# Define a class with tool methods
class DataProcessor:
    @llm_tool(description="Process data")
    def process(self, data: str) -> str:
        return f"Processed: {data}"


# Create an instance
processor = DataProcessor()


# Define a standalone tool function
@llm_tool(description="Format text")
def format_text(text: str, style: str = "plain") -> str:
    if style == "uppercase":
        return text.upper()
    elif style == "lowercase":
        return text.lower()
    return text


# Load tools from multiple sources
sources = [
    # JSON config file
    "tools_config.json",

    # Config dictionary
    {
        "func": "math:sqrt",
        "name": "square_root",
        "description": "Calculate square root"
    },

    # Class instance
    processor,

    # Module with decorated functions
    file_tools,

    # Single function
    format_text
]

# Load all tools
tools = tools_manager.load_tools_from_list(sources)

print(f"Loaded {len(tools)} tools from multiple sources")
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")
```

## File Tools Example

Here's a complete example of file operation tools with proper security:

```python
from nonix_llm import llm_tool
from nonix_llm.tools.utils import resolve_safe_path
import os
import glob


@llm_tool(
    description="Read file contents securely",
    props={"root_path": "/safe/directory"},
    hidden_props=["root_path", "bind_root"],
    param_descriptions={"file_path": "Path to the file you want to read"}
)
def read_file(file_path: str, root_path=None, bind_root=True) -> str:
    """Read file contents with path safety."""
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            bind_root=bind_root,
            must_exist=True
        )

        with open(safe_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="Write content to a file securely",
    props={"root_path": "/safe/directory"},
    hidden_props=["root_path", "bind_root"],
    param_descriptions={
        "file_path": "Path to the file you want to write to",
        "content": "Content to write to the file"
    }
)
def write_file(file_path: str, content: str, root_path=None, bind_root=True) -> str:
    """Write content to file with path safety."""
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            bind_root=bind_root,
            create_dirs=True
        )

        with open(safe_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="Find files matching a pattern in a directory",
    props={"root_path": "/safe/directory"},
    hidden_props=["root_path", "bind_root"],
    param_descriptions={
        "pattern": "Glob pattern to match files (e.g., '*.txt', '*.py')",
        "directory": "Directory to search in (defaults to current directory)",
        "recursive": "Whether to search subdirectories recursively"
    }
)
def find_files(pattern: str = "*", directory: str = ".", recursive: bool = False,
               root_path=None, bind_root=True) -> list:
    """Find files matching pattern with path safety."""
    try:
        safe_dir = resolve_safe_path(
            path=directory,
            root_path=root_path,
            bind_root=bind_root,
            must_exist=True
        )

        if recursive:
            search_pattern = os.path.join(safe_dir, "**", pattern)
            files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(safe_dir, pattern)
            files = glob.glob(search_pattern)

        # Convert absolute paths back to relative paths if needed
        if bind_root and root_path:
            files = [os.path.relpath(f, root_path) for f in files]

        return files
    except Exception as e:
        return f"Error: {str(e)}"
```

## Loading Tools from JSON Files

You can also load tools from JSON configuration files:

```python
from nonix_llm.tools.tools_manager import NxLLMToolsManager

# Create a tools manager
tools_manager = NxLLMToolsManager()

# Load tools from a JSON file
tools = tools_manager.load_tools_from_file("tools_config.json")

# Load tools from nested JSON files
tools = tools_manager.load_tools_from_directory("configs/")
```

Example JSON configuration file:

```json
{
  "tools": [
    {
      "func": "my_module:process_text",
      "name": "text_processor",
      "description": "Processes text content"
    },
    {
      "func": "file_tools:read_file",
      "props": {
        "root_path": "/safe/directory"
      },
      "hidden_props": ["root_path"]
    }
  ]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 