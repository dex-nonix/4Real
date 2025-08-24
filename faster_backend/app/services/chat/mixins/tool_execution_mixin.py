from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from ..websocket_protocol import WebSocketMixinProtocol
from ....database import AsyncSessionLocal
from ....llm.tool_runtime import list_persona_tools
from ....models.mcp_server import MCPServer
from ....models.persona import Persona
from ....service_router.decorators import expose


class ToolExecutionMixin(WebSocketMixinProtocol):
    """Mixin for tool execution and MCP operations."""

    @expose(
        '/personas/{persona_id}/tools',
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parameters": {"type": "object"}
                        }
                    }
                }
            }
        }
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
                return JSONResponse({'data': await list_persona_tools(persona.id)})
        except Exception as exc:
            return JSONResponse({'error': str(exc)}, 500)

    @expose(
        '/personas/{persona_id}/tools/execute',
        methods=['POST'],
        status_codes={200: 'OK', 403: 'Forbidden', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "Tool name to execute"},
                "args": {"type": "object", "description": "Tool arguments", "additionalProperties": True},
                "history_id": {"type": "integer", "description": "History ID for logging"},
                "message_id": {"type": "integer", "description": "Message ID for logging"}
            },
            "required": ["tool_name"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "result": {"type": "object"},
                        "error": {"type": "string"}
                    }
                }
            }
        }
    )
    @expose(
        '/mcp/servers/status',
        methods=['GET'],
        status_codes={200: 'OK'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "server_url": {"type": "string"},
                            "is_active": {"type": "boolean"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
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
