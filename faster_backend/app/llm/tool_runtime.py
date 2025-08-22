"""Stub implementation of tool_runtime for faster_backend."""


def list_persona_tools(persona_id: int):
    """Stub implementation - returns empty list for now."""
    return []


def execute_tool(tool_name: str, args: dict, persona_id: int):
    """Stub implementation - returns error for now."""
    return {"error": "Tool execution not implemented in faster_backend"}
