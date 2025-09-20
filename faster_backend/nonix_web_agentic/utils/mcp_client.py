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
        "env": server.env_json or {}
    }

    client = MultiServerMCPClient({f"server_{server_id}": server_config})
    
    try:
        await client.aconnect()
        tools = await client.alist_tools()
        return [{'name': tool.name, 'description': tool.description or ''} for tool in tools]
    finally:
        await client.aclose()


async def call_mcp_tool_by_server_id(server_id: int, tool_name: str, tool_args: Dict[str, Any] | None = None,
                                     timeout: float = 15.0) -> Dict[str, Any]:
    server = await _load_server(server_id)
    if not server:
        return {'status': 'error', 'error': 'server not found'}

    server_config = {
        "command": server.command,
        "args": server.args_json or [],
        "env": server.env_json or {}
    }

    client = MultiServerMCPClient({f"server_{server_id}": server_config})
    
    try:
        await client.aconnect()
        result = await client.acall_tool(tool_name, tool_args or {})
        return result
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    finally:
        await client.aclose()
