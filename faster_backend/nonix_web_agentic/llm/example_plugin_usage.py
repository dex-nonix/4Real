"""
Example showing how to use the LLMToolMixin for automatic LLM tool registration.

This demonstrates how simple it is to add LLM tools to any plugin using the mixin.
"""

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web_agentic.llm.llm_tool_mixin import LLMToolMixin


# Example 1: Simple plugin with LLM tools
class ExamplePlugin(BasePlugin, LLMToolMixin):
    api_services = [
        # Your API services here
    ]
    
    llm_tools = [
        ("example:hello", lambda: "Hello World!", "Simple hello world function"),
        ("example:add", lambda x, y: x + y, "Add two numbers together"),
    ]


# Example 2: Plugin with imported functions
from typing import Dict, Any

async def get_user_info(user_id: int) -> Dict[str, Any]:
    """Get user information."""
    return {"user_id": user_id, "name": "John Doe", "email": "john@example.com"}

async def list_user_files(user_id: int, category: str = None) -> Dict[str, Any]:
    """List files for a user."""
    return {"user_id": user_id, "files": ["file1.txt", "file2.pdf"], "category": category}

class UserManagementPlugin(BasePlugin, LLMToolMixin):
    api_services = [
        # User management services
    ]
    
    llm_tools = [
        ("user:get_info", get_user_info, "Get detailed information about a user"),
        ("user:list_files", list_user_files, "List files for a specific user, optionally filtered by category"),
    ]


# Example 3: Plugin with complex tool definitions
class AnalyticsPlugin(BasePlugin, LLMToolMixin):
    api_services = [
        # Analytics services
    ]
    
    llm_tools = [
        ("analytics:user_stats", lambda user_id: {"active": True, "last_login": "2024-01-01"}, "Get user analytics"),
        ("analytics:system_health", lambda: {"status": "healthy", "uptime": "99.9%"}, "Get system health status"),
        ("analytics:performance_metrics", lambda: {"response_time": "150ms", "throughput": "1000 req/s"}, "Get performance metrics"),
    ]


"""
Key Benefits of using LLMToolMixin:

1. **Declarative**: Just define an array of tools with names, functions, and descriptions
2. **Automatic**: Tools are registered automatically during plugin startup
3. **Error Handling**: Built-in validation and error handling for tool registration
4. **Logging**: Automatic logging of successful registrations and failures
5. **DRY**: No need to write boilerplate registration code
6. **Consistent**: All plugins use the same tool registration pattern
7. **Maintainable**: Easy to add/remove tools by modifying the array

Usage:
    - Inherit from both BasePlugin and LLMToolMixin
    - Define your llm_tools array with (name, function, description) tuples
    - That's it! Tools are automatically registered during startup
"""
