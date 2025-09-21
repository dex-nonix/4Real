from typing import Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import logging

from nonix_web_db import AsyncSessionLocal
from nonix_di.resolve import NxInject
from ..models.mcp_server import MCPServer
from ..models.persona import Persona
from ..llm.agentic_tool_manager import AgenticToolManager
from ..utils.mcp_client import list_mcp_server_tools_by_server_id, call_mcp_tool_by_server_id
from ..models.persona_mcp_server import PersonaMCPServer


class ToolExecutionService:
    """Service for tool execution and MCP operations."""

    agentic_tool_manager: AgenticToolManager = NxInject(AgenticToolManager)

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    async def list_persona_tools(self, persona_id: int):
        """Get available tools for a specific persona."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(Persona).where(Persona.id == persona_id)
            result = await db_session.execute(stmt)
            persona = result.scalar_one_or_none()

            if not persona:
                raise ValueError('Persona not found')
            return await self.agentic_tool_manager.list_persona_tools(persona.id)

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
                # Execute the actual tool using the agentic tool manager
                tool_result = await self.agentic_tool_manager.execute_tool(
                    persona_id=persona_id,
                    tool_name=tool_name,
                    parameters=parameters
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

    async def discover_mcp_tools_for_persona(self, persona_id: int):
        """Return MCP tools for each active persona-assigned server."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(PersonaMCPServer).options(
                joinedload(PersonaMCPServer.mcp_server)
            ).where(PersonaMCPServer.persona_id == persona_id,
                   PersonaMCPServer.is_active)
            result = await db_session.execute(stmt)
            links = result.scalars().all()

        out = []
        for link in links:
            tools = await list_mcp_server_tools_by_server_id(link.mcp_server_id)
            out.append({
                'persona_mcp_server_id': link.id,
                'mcp_server_id': link.mcp_server_id,
                'mcp_server_name': getattr(link.mcp_server, 'name', None),
                'tools': tools
            })
        return out


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
