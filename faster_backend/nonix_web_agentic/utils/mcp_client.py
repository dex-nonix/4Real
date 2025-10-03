import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from langchain_mcp_adapters.client import MultiServerMCPClient

from nonix_web_db import AsyncSessionLocal
from ..models.mcp_server import MCPServer


class CachedMCPClient:
    def __init__(self, client: MultiServerMCPClient, config_hash: str):
        self.client = client
        self.config_hash = config_hash
        self.last_accessed = datetime.now()
        self.server_ids = set()


_mcp_client_cache: Dict[str, CachedMCPClient] = {}
_cache_lock = asyncio.Lock()
_IDLE_TIMEOUT = timedelta(minutes=10)


async def _load_server(server_id: int) -> Optional[MCPServer]:
    async with AsyncSessionLocal() as db:
        return await db.get(MCPServer, server_id)


def _generate_config_hash(command: str, args: list, env: dict, transport: str, url: str) -> str:
    config_str = f"{command}|{json.dumps(args, sort_keys=True)}|{json.dumps(env, sort_keys=True)}|{transport}|{url}"
    return hashlib.sha256(config_str.encode()).hexdigest()


async def _cleanup_idle_clients():
    async with _cache_lock:
        now = datetime.now()
        to_remove = []
        for config_hash, cached_client in _mcp_client_cache.items():
            if now - cached_client.last_accessed > _IDLE_TIMEOUT:
                to_remove.append(config_hash)

        for config_hash in to_remove:
            del _mcp_client_cache[config_hash]


def build_mcp_server_config(server) -> dict:
    transport = server.transport or "stdio"

    if transport == "stdio":
        return {
            "command": server.command,
            "args": server.args_json or [],
            "env": server.env_json or {},
            "transport": "stdio"
        }
    elif transport in ["websocket", "http","streamable_http"]:
        return {
            "url": server.url,
            "transport": transport
        }
    else:
        raise ValueError(f"Unsupported transport: {transport}")


async def _get_or_create_cached_client(server_id: int) -> Optional[MultiServerMCPClient]:
    server = await _load_server(server_id)
    if not server:
        return None

    await _cleanup_idle_clients()

    config_hash = _generate_config_hash(
        server.command or "",
        server.args_json or [],
        server.env_json or {},
        server.transport or "stdio",
        server.url or ""
    )

    async with _cache_lock:
        if config_hash in _mcp_client_cache:
            cached_client = _mcp_client_cache[config_hash]
            cached_client.last_accessed = datetime.now()
            cached_client.server_ids.add(server_id)
            return cached_client.client

        server_config = build_mcp_server_config(server)

        client = MultiServerMCPClient({f"server_{server_id}": server_config})
        cached_client = CachedMCPClient(client, config_hash)
        cached_client.server_ids.add(server_id)
        _mcp_client_cache[config_hash] = cached_client

        return client


async def list_mcp_server_tools_by_server_id(server_id: int, timeout: float = 8.0) -> List[Dict[str, Any]]:
    client = await _get_or_create_cached_client(server_id)
    if not client:
        return []

    tools = await client.get_tools()
    return [{'name': tool.name, 'description': tool.description or ''} for tool in tools]


async def call_mcp_tool_by_server_id(server_id: int, tool_name: str, tool_args: Dict[str, Any] | None = None,
                                     timeout: float = 15.0) -> Dict[str, Any]:
    client = await _get_or_create_cached_client(server_id)
    if not client:
        return {'status': 'error', 'error': 'server not found'}

    try:
        async with client.session(f"server_{server_id}") as session:
            result = await session.call_tool(tool_name, tool_args or {})
            return result
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


async def get_external_tool_schema(server_id: int, tool_name: str) -> Dict[str, Any]:
    client = await _get_or_create_cached_client(server_id)
    if not client:
        return {'name': tool_name, 'description': '', 'parameters': []}

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
