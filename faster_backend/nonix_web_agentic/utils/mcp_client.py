from typing import List, Dict, Any, Optional
import os

from nonix_web_db import AsyncSessionLocal

from ..models.mcp_server import MCPServer

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


async def _load_server(server_id: int) -> Optional[MCPServer]:
    async with AsyncSessionLocal() as db:
        return await db.get(MCPServer, server_id)


async def list_mcp_server_tools_by_server_id(server_id: int, timeout: float = 8.0) -> List[Dict[str, Any]]:
    server = await _load_server(server_id)
    if not server:
        return []

    server_params = StdioServerParameters(
        command=server.command,
        args=server.args_json or [],
        env=server.env_json or None,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        session = ClientSession(read_stream, write_stream)
        await session.initialize()
        result = await session.list_tools()
        tools = getattr(result, 'tools', []) if result is not None else []
        return [{'name': t.name, 'description': t.description or ''} for t in tools]


async def call_mcp_tool_by_server_id(server_id: int, tool_name: str, tool_args: Dict[str, Any] | None = None,
                                      timeout: float = 15.0) -> Dict[str, Any]:
    server = await _load_server(server_id)
    if not server:
        return {'status': 'error', 'error': 'server not found'}

    server_params = StdioServerParameters(
        command=server.command,
        args=server.args_json or [],
        env=server.env_json or None,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        session = ClientSession(read_stream, write_stream)
        await session.initialize()
        return await session.call_tool(tool_name, tool_args or {})
