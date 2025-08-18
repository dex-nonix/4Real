from __future__ import annotations

from typing import Any, Callable, Dict
from functools import partial
import inspect

from ..models.internal_tool import InternalTool
from ..models.persona_tool_access import PersonaToolAccess
from ..models.persona import Persona
from .internal_tool_registry import registry as internal_tool_registry


def _pattern_matches(pattern: str, name: str) -> bool:
    if pattern.endswith(':*'):
        return name.startswith(pattern[:-2] + ':')
    return pattern == name


def build_persona_tool_map(persona_id: int) -> Dict[str, Callable[..., Any]]:
    """Return a persona-scoped tool map of qualified_name -> callable.

    - Applies allowlist via PersonaToolAccess patterns over active InternalTools
    - If persona.artist_id is set and a tool's first parameter is 'artist_id', expose a partial with artist_id pre-bound
    - Keeps global registry immutable; returns a new dict per call
    """
    persona = Persona.query.filter_by(id=persona_id).first()
    artist_id = getattr(persona, 'artist_id', None) if persona else None

    tools: Dict[str, Callable[..., Any]] = {}
    active_tools = InternalTool.query.filter_by(is_active=True).all()
    patterns = PersonaToolAccess.query.filter_by(persona_id=persona_id, allow=True).all()

    for tool in active_tools:
        qname = tool.qualified_name
        if not any(_pattern_matches(p.pattern, qname) for p in patterns):
            continue
        func = internal_tool_registry.get(qname)
        if not callable(func):
            continue

        # If persona has artist_id and the first parameter is artist_id, bind it via partial
        if artist_id is not None:
            try:
                sig = inspect.signature(func)
                params = list(sig.parameters.values())
                if params and params[0].name == 'artist_id':
                    tools[qname] = partial(func, artist_id)
                    continue
            except Exception:  # noqa: BLE001
                pass

        tools[qname] = func

    return tools


def list_persona_tools(persona_id: int) -> list[str]:
    return sorted(list(build_persona_tool_map(persona_id).keys()))


def execute_tool(persona_id: int, tool_name: str, args: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Execute a persona-scoped tool by name with provided args.

    The callable may be a partial; args are passed through without mutation.
    """
    tool_map = build_persona_tool_map(persona_id)
    func = tool_map.get(tool_name)
    if not callable(func):
        return {'status': 'error', 'error': 'Tool not allowed or not found'}
    
    try:
        result = func(**(args or {})) if (args) else func()
        return {'status': 'success', 'result': result}
    except Exception as exc:  # noqa: BLE001
        return {'status': 'error', 'error': str(exc)}


