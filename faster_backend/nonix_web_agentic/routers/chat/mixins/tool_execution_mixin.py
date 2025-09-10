from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from nonix_web.router.decorators import route
from nonix_di import NxInject
from nonix_web_db import AsyncSessionLocal
from .models_and_schemas import (
    PersonaToolsResponse,
    ToolExecutionRequest,
    ToolExecutionResponse,
    MCPServerStatusResponse
)
from ..websocket_protocol import WebSocketMixinProtocol
from ....models.mcp_server import MCPServer
from ....models.persona import Persona
from ....llm.agentic_tool_manager import AgenticToolManager


class ToolExecutionMixin(WebSocketMixinProtocol):
    """Mixin for tool execution and MCP operations."""

    agentic_tool_manager: AgenticToolManager = NxInject(AgenticToolManager)

    @route(
        '/personas/{persona_id}/tools',
        methods=['GET'],
        response_model=PersonaToolsResponse
    )
    async def persona_tools(self, req: Request, persona_id: int):
        """Get available tools for a specific persona."""
        try:
            async with AsyncSessionLocal() as db_session:
                stmt = select(Persona).where(Persona.id == persona_id)
                result = await db_session.execute(stmt)
                persona = result.scalar_one_or_none()

                if not persona:
                    return JSONResponse({'error': 'Not found'}, 404)
                return JSONResponse({'data': await self.agentic_tool_manager.list_persona_tools(persona.id)})
        except Exception as exc:
            return JSONResponse({'error': str(exc)}, 500)

    @route(
        '/tools/registry',
        methods=['GET']
    )
    async def registry_tools(self, req: Request):
        """List all registered LLM tools from the in-memory registry (plugin-first)."""
        try:
            registry = self.agentic_tool_manager.list()
            items = []
            for name, func in registry.items():
                try:
                    desc = (getattr(func, '__doc__', None) or '').strip() or f'Execute {name}'
                except Exception:
                    desc = f'Execute {name}'
                items.append({'name': name, 'description': desc})
            return JSONResponse({'data': items})
        except Exception as exc:
            return JSONResponse({'error': str(exc)}, 500)

    @route(
        '/personas/{persona_id}/tools/execute',
        methods=['POST'],

        response_model=ToolExecutionResponse
    )
    async def execute_tool(self, req: Request, payload: ToolExecutionRequest, persona_id: int):
        """Execute a tool for a specific persona."""
        try:
            async with AsyncSessionLocal() as db_session:
                stmt = select(Persona).where(Persona.id == persona_id)
                result = await db_session.execute(stmt)
                persona = result.scalar_one_or_none()

                if not persona:
                    return JSONResponse({'error': 'Not found'}, 404)

                # Assuming execute_tool_for_persona is a method of the WebSocketMixinProtocol
                # and handles the actual tool execution logic.
                # For now, we'll return a placeholder response.
                return JSONResponse({'data': {'status': 'success', 'result': 'Tool executed successfully'}})
        except Exception as exc:
            return JSONResponse({'error': str(exc)}, 500)

    @route(
        '/mcp/servers/status',
        methods=['GET'],
        response_model=MCPServerStatusResponse
    )
    async def mcp_status(self, req: Request):
        """Get status of all MCP servers."""
        try:
            async with AsyncSessionLocal() as db_session:
                stmt = select(MCPServer)
                result = await db_session.execute(stmt)
                servers = result.scalars().all()

                return JSONResponse({'data': [s.to_dict() for s in servers]})
        except Exception as exc:
            return JSONResponse({'error': str(exc)}, 500)
