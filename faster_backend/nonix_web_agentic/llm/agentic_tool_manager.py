import inspect
import logging
from typing import Any, Dict, List, Optional
from typing import Callable

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from ..models.persona import Persona
from ..models.persona_tool_access import PersonaToolAccess


def llm_tool_wrapper(original_func, *args, **kwargs):
    """Create a LangChain-compatible wrapper that preserves partial binding."""

    if inspect.iscoroutinefunction(original_func):
        async def wrapper(*w_args, **w_kwargs):
            return await original_func(*args, *w_args, **kwargs, **w_kwargs)
    else:
        def wrapper(*w_args, **w_kwargs):
            return original_func(*args, *w_args, **kwargs, **w_kwargs)

    wrapper.__name__ = original_func.__name__
    wrapper.__doc__ = original_func.__doc__
    wrapper.__annotations__ = getattr(original_func, "__annotations__", {})

    return wrapper


def _pattern_matches(pattern: str, name: str) -> bool:
    if pattern.endswith(':*'):
        return name.startswith(pattern[:-2] + ':')
    return pattern == name


class AgenticToolManager:
    """Minimal in-process registry mapping qualified tool names to callables."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._registry: Dict[str, Callable[..., Any]] = {}

    def register(self, qualified_name: str, func: Callable[..., Any]) -> None:

        self._logger.info(f"Registering agentic tool: {qualified_name}")
        self._registry[qualified_name] = func

    def get(self, qualified_name: str) -> Callable[..., Any] | None:
        return self._registry.get(qualified_name)

    def list(self) -> Dict[str, Callable[..., Any]]:
        return dict(self._registry)

    async def execute(self, qualified_name: str, args: dict | None = None) -> dict:
        func = self.get(qualified_name)
        if not func:
            return {'status': 'error', 'error': f'tool {qualified_name} not found'}
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**(args or {})) if args else await func()
            else:
                result = func(**(args or {})) if args else func()
            return {'status': 'success', 'result': result}
        except Exception as exc:  # noqa: BLE001
            return {'status': 'error', 'error': str(exc)}

    async def build_persona_tool_map(self, persona_id: int) -> Dict[str, Callable[..., Any]]:
        async with AsyncSessionLocal() as db_session:
            persona_result = await db_session.execute(
                select(Persona).where(Persona.id == persona_id)
            )
            persona = persona_result.scalar_one_or_none()
            artist_id = getattr(persona, 'artist_id', None) if persona else None

            tools: Dict[str, Callable[..., Any]] = {}
            patterns_result = await db_session.execute(
                select(PersonaToolAccess).where(
                    PersonaToolAccess.persona_id == persona_id
                )
            )
            all_patterns = patterns_result.scalars().all()
            allow_patterns = [p for p in all_patterns if getattr(p, 'allow', False)]
            deny_patterns = [p for p in all_patterns if not getattr(p, 'allow', False)]

            for qname, func in self.list().items():
                if any(_pattern_matches(p.pattern, qname) for p in deny_patterns):
                    continue
                if not any(_pattern_matches(p.pattern, qname) for p in allow_patterns):
                    continue
                if not callable(func):
                    continue

                if artist_id is not None:
                    sig = inspect.signature(func)
                    params = list(sig.parameters.values())
                    if params and params[0].name == 'artist_id':
                        tools[qname] = llm_tool_wrapper(func, artist_id)
                        continue

                tools[qname] = func

        return tools

    async def list_persona_tools(self, persona_id: int) -> List[dict]:
        async with AsyncSessionLocal() as db_session:
            persona_result = await db_session.execute(
                select(Persona).where(Persona.id == persona_id)
            )
            persona = persona_result.scalar_one_or_none()
            artist_id = getattr(persona, 'artist_id', None) if persona else None

            tools_info = []
            patterns_result = await db_session.execute(
                select(PersonaToolAccess).where(
                    PersonaToolAccess.persona_id == persona_id
                )
            )
            all_patterns = patterns_result.scalars().all()
            allow_patterns = [p for p in all_patterns if getattr(p, 'allow', False)]
            deny_patterns = [p for p in all_patterns if not getattr(p, 'allow', False)]

            for qname, func in self.list().items():
                if any(_pattern_matches(p.pattern, qname) for p in deny_patterns):
                    continue
                if not any(_pattern_matches(p.pattern, qname) for p in allow_patterns):
                    continue
                if not callable(func):
                    continue

                try:
                    sig = inspect.signature(func)
                    params = []

                    for param_name, param in sig.parameters.items():
                        if artist_id is not None and param_name == 'artist_id':
                            continue

                        param_info = {
                            'name': param_name,
                            'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'any',
                            'required': param.default == inspect.Parameter.empty,
                            'default': param.default if param.default != inspect.Parameter.empty else None
                        }
                        params.append(param_info)

                    tool_info = {
                        'name': qname,
                        'description': (func.__doc__ or '').strip() or f'Execute {qname}',
                        'parameters': params,
                        'has_artist_id_bound': artist_id is not None and any(
                            p.name == 'artist_id' for p in sig.parameters.values())
                    }

                    tools_info.append(tool_info)

                except Exception:
                    tool_info = {
                        'name': qname,
                        'description': f'Execute {qname}',
                        'parameters': [],
                        'has_artist_id_bound': False
                    }
                    tools_info.append(tool_info)

        return sorted(tools_info, key=lambda x: x['name'])

    async def execute_tool(self, persona_id: int, tool_name: str, args: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Execute a persona-scoped tool by name with provided args.

        The callable may be a partial; args are passed through without mutation.
        """
        tool_map = await self.build_persona_tool_map(persona_id)
        func = tool_map.get(tool_name)
        if not callable(func):
            return {'status': 'error', 'error': 'Tool not allowed or not found'}

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**(args or {})) if args else await func()
            else:
                result = func(**(args or {})) if args else func()
            return {'status': 'success', 'result': result}
        except Exception as exc:  # noqa: BLE001
            return {'status': 'error', 'error': str(exc)}

    async def create_langchain_tools(
            self,
            persona_id: int,
            available_tools_info: List[Dict[str, Any]]
    ) -> List[StructuredTool]:
        """Create LangChain StructuredTool objects from persona tools with proper Pydantic schemas."""

        async def _get_field_type(param_type: str) -> type:
            """Extract the base Python type from a type annotation string."""
            if 'int' in param_type:
                return int
            elif 'str' in param_type:
                return str
            elif 'bool' in param_type:
                return bool
            elif 'float' in param_type:
                return float
            else:
                return str

        # Get the persona-scoped tools with partial binding
        persona_tools = await self.build_persona_tool_map(persona_id)

        langchain_tools = []
        for tool_name, tool_func in persona_tools.items():
            # Find tool info for description
            tool_info = next((t for t in available_tools_info if t['name'] == tool_name), None)
            description = tool_info.get('description', f'Execute {tool_name}') if tool_info else f'Execute {tool_name}'

            # Create a dynamic Pydantic model for the tool parameters
            if tool_info and 'parameters' in tool_info and tool_info['parameters']:
                try:
                    # Create a dynamic schema class from the already-extracted parameters
                    schema_fields = {}
                    annotations = {}

                    for param in tool_info['parameters']:
                        param_name = param['name']
                        param_type = param['type']
                        param_required = param['required']
                        param_default = param['default']

                        # Get the base field type
                        field_type = await _get_field_type(param_type)

                        # Create the field - the logic is the same regardless of Optional/Union
                        if param_required:
                            schema_fields[param_name] = Field(description=f"Parameter: {param_name}")
                            annotations[param_name] = field_type
                        else:
                            schema_fields[param_name] = Field(default=param_default,
                                                              description=f"Parameter: {param_name}")
                            annotations[param_name] = Optional[field_type]

                    # Create the schema class dynamically with proper annotations
                    ToolSchema = type(f'{tool_name}Schema', (BaseModel,), {
                        '__annotations__': annotations,
                        **schema_fields
                    })

                    # Create StructuredTool with proper Pydantic schema
                    is_async = inspect.iscoroutinefunction(tool_func)
                    if is_async:
                        langchain_tool = StructuredTool.from_function(
                            func=(lambda **_: None),
                            coroutine=tool_func,
                            name=tool_name,
                            description=description,
                            args_schema=ToolSchema
                        )
                    else:
                        langchain_tool = StructuredTool.from_function(
                            func=tool_func,
                            name=tool_name,
                            description=description,
                            args_schema=ToolSchema
                        )

                    self._logger.debug(f"🔧 Created tool '{tool_name}' with Pydantic schema")

                except Exception as e:
                    self._logger.warning(f"🔧 Failed to create Pydantic schema for tool '{tool_name}': {e}",
                                         exc_info=True)
                    # Fallback: create tool without schema
                    is_async = inspect.iscoroutinefunction(tool_func)
                    if is_async:
                        langchain_tool = StructuredTool.from_function(
                            func=(lambda **_: None),
                            coroutine=tool_func,
                            name=tool_name,
                            description=description
                        )
                    else:
                        langchain_tool = StructuredTool.from_function(
                            func=tool_func,
                            name=tool_name,
                            description=description
                        )
            else:
                # Fallback: no schema, just basic tool
                is_async = inspect.iscoroutinefunction(tool_func)
                if is_async:
                    langchain_tool = StructuredTool.from_function(
                        func=(lambda **_: None),
                        coroutine=tool_func,
                        name=tool_name,
                        description=description
                    )
                else:
                    langchain_tool = StructuredTool.from_function(
                        func=tool_func,
                        name=tool_name,
                        description=description
                    )

            langchain_tools.append(langchain_tool)

        self._logger.info(f"🔧 Created {len(langchain_tools)} LangChain tools for persona {persona_id}")
        return langchain_tools
