from typing import List, Dict, Any, Optional
import os

from nonix_web_db import AsyncSessionLocal

from ..models.mcp_server import MCPServer

# MCP client lib imports (may require installation in environment)
from mcp.client.stdio import StdioConnector
from mcp.client.session import ClientSession


async def _load_server(server_id: int) -> Optional[MCPServer]:
    async with AsyncSessionLocal() as db:
        return await db.get(MCPServer, server_id)


async def list_mcp_server_tools_by_server_id(server_id: int, timeout: float = 8.0) -> List[Dict[str, Any]]:
    server = await _load_server(server_id)
    if not server:
        return []

    args = server.args_json or []
    env = os.environ.copy()
    if server.env_json:
        env.update(server.env_json)

    async with StdioConnector(command=server.command, args=args, env=env).connect() as (reader, writer):
        async with ClientSession(reader, writer, request_timeout=timeout) as session:
            await session.initialize()
            resp = await session.tools.list()
            tools = getattr(resp, 'tools', []) if resp is not None else []
            return [{'name': getattr(t, 'name', None), 'description': getattr(t, 'description', '') or ''} for t in tools]


async def call_mcp_tool_by_server_id(server_id: int, tool_name: str, tool_args: Dict[str, Any] | None = None,
                                      timeout: float = 15.0) -> Dict[str, Any]:
    server = await _load_server(server_id)
    if not server:
        return {'status': 'error', 'error': 'server not found'}

    args = server.args_json or []
    env = os.environ.copy()
    if server.env_json:
        env.update(server.env_json)

    async with StdioConnector(command=server.command, args=args, env=env).connect() as (reader, writer):
        async with ClientSession(reader, writer, request_timeout=timeout) as session:
            await session.initialize()
            return await session.tools.call(tool_name, tool_args or {})
