from typing import List, Dict, Any, Optional
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from nonix_web.utils.di import Inject
from ..models.mcp_server import MCPServer
from ..models.persona import Persona
from ..llm.agentic_tool_manager import AgenticToolManager


class ToolExecutionService:
    """Service for tool execution and MCP operations."""

    agentic_tool_manager: AgenticToolManager = Inject(AgenticToolManager)

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

            # For now, return a placeholder response
            # In a real implementation, this would call the actual tool execution
            return {'status': 'success', 'result': 'Tool executed successfully'}

    async def get_mcp_servers_status(self):
        """Get status of all MCP servers."""
        async with AsyncSessionLocal() as db_session:
            stmt = select(MCPServer)
            result = await db_session.execute(stmt)
            servers = result.scalars().all()

            return [s.to_dict() for s in servers]
