from typing import List, Dict, Any, Optional

from langchain_mcp_adapters.client import MultiServerMCPClient

from nonix_web_db import AsyncSessionLocal
from ..models.mcp_server import MCPServer


async def _load_server(server_id: int) -> Optional[MCPServer]:
    async with AsyncSessionLocal() as db:
        return await db.get(MCPServer, server_id)


async def list_mcp_server_tools_by_server_id(server_id: int, timeout: float = 8.0) -> List[Dict[str, Any]]:
    server = await _load_server(server_id)
    if not server:
        return []

    server_config = {
        "command": server.command,
        "args": server.args_json or [],
        "env": server.env_json or {},
        "transport": "stdio"
    }

    client = MultiServerMCPClient({f"server_{server_id}": server_config})
    
    tools = await client.get_tools()
    return [{'name': tool.name, 'description': tool.description or ''} for tool in tools]


async def call_mcp_tool_by_server_id(server_id: int, tool_name: str, tool_args: Dict[str, Any] | None = None,
                                     timeout: float = 15.0) -> Dict[str, Any]:
    server = await _load_server(server_id)
    if not server:
        return {'status': 'error', 'error': 'server not found'}

    server_config = {
        "command": server.command,
        "args": server.args_json or [],
        "env": server.env_json or {},
        "transport": "stdio"
    }

    client = MultiServerMCPClient({f"server_{server_id}": server_config})
    
    try:
        async with client.session(f"server_{server_id}") as session:
            result = await session.call_tool(tool_name, tool_args or {})
            return result
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


async def get_external_tool_schema(server_id: int, tool_name: str) -> Dict[str, Any]:
    server = await _load_server(server_id)
    if not server:
        return {'name': tool_name, 'description': '', 'parameters': []}
    server_config = {
        "command": server.command,
        "args": server.args_json or [],
        "env": server.env_json or {},
        "transport": "stdio"
    }
    client = MultiServerMCPClient({f"server_{server_id}": server_config})
    tools = await client.get_tools()
    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        return {'name': tool_name, 'description': '', 'parameters': []}
    parameters = []
    if getattr(tool, 'inputSchema', None) and 'properties' in tool.inputSchema:
        schema = tool.inputSchema
        for param_name, param_schema in schema['properties'].items():
            parameters.append({
                'name': param_name,
                'type': param_schema.get('type', 'string'),
                'required': param_name in schema.get('required', []),
                'default': param_schema.get('default'),
                'description': param_schema.get('description', '')
            })
    return {
        'name': tool.name,
        'description': tool.description or '',
        'parameters': parameters
    }
