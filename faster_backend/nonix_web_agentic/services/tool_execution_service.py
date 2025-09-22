from typing import Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import logging

from nonix_web.web_socket_service import NxWebServerWebSocketService
from nonix_web_db import AsyncSessionLocal
from nonix_di.resolve import NxInject
from ..models.mcp_server import MCPServer
from ..models.persona import Persona
from ..llm.agentic_tool_manager import AgenticToolManager
from ..utils.mcp_client import list_mcp_server_tools_by_server_id, call_mcp_tool_by_server_id
from ..models.persona_mcp_server import PersonaMCPServer
from ..utils.mcp_client import get_external_tool_schema


class ToolExecutionService:
    """Service for tool execution and MCP operations."""

    agentic_tool_manager: AgenticToolManager = NxInject(AgenticToolManager)
    web_socket_service: NxWebServerWebSocketService = NxInject(NxWebServerWebSocketService)

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    async def _get_persona_mcp_links(self, persona_id: int):
        """Shared helper: Get active MCP server links for a persona."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(PersonaMCPServer).options(
                joinedload(PersonaMCPServer.mcp_server)
            ).where(PersonaMCPServer.persona_id == persona_id,
                   PersonaMCPServer.is_active)
            result = await db_session.execute(stmt)
            return result.scalars().all()

    async def list_registry_tools(self):
        """List all registered LLM tools from the in-memory registry (plugin-first)."""
        registry = self.agentic_tool_manager.list()
        items = []
        for name, func in registry.items():
            try:
                desc = (getattr(func, '__doc__', None) or '').strip() or f'Execute {name}'
            except Exception:
                desc = f'Execute {name}'
            items.append({'name': name, 'description': desc})
        return items

    async def get_tools(self, persona_id: int):
        internal_namespaces = await self.get_internal_tools(persona_id)
        external_namespaces = await self.get_external_tools(persona_id)
        all_namespaces = internal_namespaces + external_namespaces
        return all_namespaces

    async def get_internal_tools(self, persona_id: int):
        internal_tools = await self.agentic_tool_manager.list_persona_tools(persona_id)
        namespace_map = {}
        for tool in internal_tools:
            namespace, function_name = tool['name'].split(':', 1)
            if namespace not in namespace_map:
                namespace_map[namespace] = {
                    'namespace': namespace,
                    'description': f'{namespace} operations',
                    'is_external': False,
                    'tools': []
                }
            namespace_map[namespace]['tools'].append({
                'name': function_name,
                'description': tool['description'],
                'parameters': tool['parameters']
            })
        return list(namespace_map.values())

    async def get_external_tools(self, persona_id: int):
        external_servers = await self.get_external_servers(persona_id)
        namespace_map = {}
        for server in external_servers:
            namespace = server['mcp_server_name']
            if namespace not in namespace_map:
                namespace_map[namespace] = {
                    'namespace': namespace,
                    'description': f'{namespace} operations',
                    'is_external': True,
                    'tools': []
                }
            # Use basic tool info - don't fetch schemas upfront to avoid hanging
            for tool in server['tools']:
                namespace_map[namespace]['tools'].append({
                    'name': tool['name'],
                    'description': tool['description'],
                    'parameters': []  # Will be fetched on-demand when tool is selected
                })
        return list(namespace_map.values())

    async def get_external_servers(self, persona_id: int):
        links = await self._get_persona_mcp_links(persona_id)
        out = []
        for link in links:
            tools = await list_mcp_server_tools_by_server_id(link.mcp_server_id)
            out.append({
                'persona_mcp_server_id': link.id,
                'mcp_server_id': link.mcp_server_id,
                'mcp_server_name': link.mcp_server.name if link.mcp_server else None,
                'tools': tools
            })
        return out

    async def get_tool_schema(self, server_id: int, tool_name: str) -> Dict[str, Any]:
        return await get_external_tool_schema(server_id, tool_name)

    async def get_persona_tool_schema(self, persona_id: int, tool_name: str) -> Dict[str, Any]:
        """Get schema for any tool (internal or external) by full name."""
        if ':' not in tool_name:
            # Internal tool - get from agentic tool manager
            tools_info = await self.agentic_tool_manager.list_persona_tools(persona_id)
            tool_info = next((t for t in tools_info if t['name'] == tool_name), None)
            if tool_info:
                return {'name': tool_info['name'], 'description': tool_info['description'], 'parameters': tool_info['parameters']}
            else:
                return {'name': tool_name, 'description': '', 'parameters': []}
        else:
            # External tool - parse namespace and get schema
            namespace, actual_tool_name = tool_name.split(':', 1)
            links = await self._get_persona_mcp_links(persona_id)
            link = next((l for l in links if l.mcp_server and l.mcp_server.name == namespace), None)
            if link:
                return await self.get_tool_schema(link.mcp_server_id, actual_tool_name)
            else:
                return {'name': tool_name, 'description': '', 'parameters': []}

    async def execute_tool_for_persona(self, persona_id: int, tool_name: str, parameters: Dict[str, Any]):
        """Execute a tool for a specific persona."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(Persona).where(Persona.id == persona_id)
            result = await db_session.execute(stmt)
            persona = result.scalar_one_or_none()

            if not persona:
                raise ValueError('Persona not found')

            # Emit WebSocket event for tool execution start
            await self.web_socket_service.send_ws_message(
                f'persona/{persona_id}',
                {
                    'event': 'tool_status',
                    'data': {
                        'tool_name': tool_name,
                        'status': 'running',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
            )

            try:
                if self.agentic_tool_manager.get(tool_name) is not None:
                    tool_result = await self.agentic_tool_manager.execute_tool(
                        persona_id=persona_id,
                        tool_name=tool_name,
                        parameters=parameters
                    )
                else:
                    tool_result = await self.execute_external_tool(
                        persona_id,
                        tool_name,
                        parameters
                    )

                result = {
                    'status': 'success',
                    'result': tool_result,
                    'tool_name': tool_name,
                    'execution_time': 'completed'
                }

                # Emit WebSocket event for tool execution completion
                await self.web_socket_service.send_ws_message(
                    f'persona/{persona_id}',
                    {
                        'event': 'tool_status',
                        'data': {
                            'tool_name': tool_name,
                            'status': 'completed',
                            'result': tool_result,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    }
                )

                return result
            except Exception as e:
                # Emit WebSocket event for tool execution error
                await self.web_socket_service.send_ws_message(
                    f'persona/{persona_id}',
                    {
                        'event': 'tool_status',
                        'data': {
                            'tool_name': tool_name,
                            'status': 'failed',
                            'error': str(e),
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    }
                )
                raise

    async def call_persona_mcp_tool(self, persona_id: int, persona_mcp_server_id: int,
                                    tool_name: str, tool_args: Dict[str, Any] | None = None):
        """Call a tool on a persona-assigned MCP server (verifies assignment)."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(PersonaMCPServer).where(PersonaMCPServer.id == persona_mcp_server_id,
                                                  PersonaMCPServer.persona_id == persona_id,
                                                  PersonaMCPServer.is_active)
            result = await db_session.execute(stmt)
            link = result.scalar_one_or_none()
            if not link:
                raise ValueError('MCP server not assigned to persona or inactive')

        return await call_mcp_tool_by_server_id(link.mcp_server_id, tool_name, tool_args)


    async def get_mcp_servers_status(self):
        """Get status of all MCP servers."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(MCPServer)
            result = await db_session.execute(stmt)
            servers = result.scalars().all()

            return [s.to_dict() for s in servers]

    async def execute_external_tool(self, persona_id: int, tool_name: str, parameters: Dict[str, Any]):
        if ':' not in tool_name:
            raise ValueError('Tool name must have namespace: server_name:tool_name')
        server_name, actual_tool_name = tool_name.split(':', 1)
        links = await self._get_persona_mcp_links(persona_id)
        link = next((l for l in links if l.mcp_server and l.mcp_server.name == server_name), None)
        if not link:
            raise ValueError(f'External server {server_name} not assigned to persona {persona_id}')
        return await call_mcp_tool_by_server_id(link.mcp_server_id, actual_tool_name, parameters)
