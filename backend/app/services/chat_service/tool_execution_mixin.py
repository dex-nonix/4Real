from __future__ import annotations

from typing import Any, Dict, List
from flask import jsonify, Request
from ...decorators import expose
from ... import db
from ...models.persona import Persona
from ...models.mcp_server import MCPServer
from ...models.tool_invocation_log import ToolInvocationLog
from ...models.chat_message import ChatMessage
from ..tool_runtime import build_persona_tool_map, execute_tool, list_persona_tools
from datetime import datetime


class ToolExecutionMixin:
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
    def persona_tools(self, req: Request, persona_id: int):
        """Get available tools for a specific persona."""
        try:
            persona = Persona.query.filter_by(id=persona_id).first()
            if not persona:
                return jsonify({'error': 'Not found'}), 404
            return jsonify({'data': list_persona_tools(persona.id)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

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
    def persona_tool_execute(self, req: Request, persona_id: int):
        """Execute a tool for a specific persona."""
        try:
            payload = req.get_json(silent=True) or {}
            tool_name = payload.get('tool_name')  # Changed from 'tool' to 'tool_name'
            tool_args = payload.get('args') or {}
            history_id = payload.get('history_id')
            user_message_id = payload.get('message_id')

            persona = Persona.query.filter_by(id=persona_id).first()
            if not persona:
                return jsonify({'error': 'Not found'}), 404
            tools = build_persona_tool_map(persona.id)
            if tool_name not in tools:
                return jsonify({'error': 'Tool not allowed'}), 403

            # Only create log entry if we have required fields
            log = None
            if history_id is not None:
                log = ToolInvocationLog(
                    history_id=history_id,
                    message_id=user_message_id or 0,  # Use 0 as default if None
                    tool_name=tool_name,
                    input_json=tool_args,
                    status='started'
                )
                db.session.add(log)
                db.session.commit()

            exec_result = execute_tool(persona.id, tool_name, tool_args)
            
            # Update log if it exists
            if log:
                log.status = 'success' if exec_result.get('status') == 'success' else 'error'
                log.output_json = exec_result
                db.session.commit()

            if history_id:
                # Create a proper tool message that matches ToolMessage component expectations
                tool_msg = ChatMessage(
                    history_id=history_id, 
                    role='tool', 
                    message_type='tool',  # Changed from 'tool_result' to 'tool'
                    content_json={
                        'toolName': tool_name,
                        'toolParams': tool_args,
                        'executionStatus': 'success' if exec_result.get('status') == 'success' else 'error',
                        'result': exec_result,
                        'executedBy': 'user',  # Mark as user-executed
                        'executionTime': datetime.utcnow().isoformat()
                    }
                )
                db.session.add(tool_msg)
                db.session.commit()

            return jsonify({'data': exec_result})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

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
    def mcp_status(self, req: Request):
        """Get status of all MCP servers."""
        try:
            servers = MCPServer.query.all()
            return jsonify({'data': [s.to_dict() for s in servers]})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500 