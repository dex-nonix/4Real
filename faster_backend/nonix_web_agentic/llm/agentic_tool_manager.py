import inspect
import logging
from typing import Any, Dict, List, Optional
from typing import Callable

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from ..models.persona_mcp_server import PersonaMCPServer
from langchain_mcp_adapters.client import MultiServerMCPClient
from ..utils.mcp_client import call_mcp_tool_by_server_id

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


def _get_field_type(param_type: str) -> type:
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

def _pattern_matches(pattern: str, name: str) -> bool:
    if pattern.endswith(':*'):
        return name.startswith(pattern[:-2] + ':')
    return pattern == name


def make_agent_tool_wrapper(manager, persona_id: int, tool_name: str):
    async def wrapped_tool(**kwargs):
        exec_result = await manager.execute_tool(persona_id, tool_name, kwargs or {})
        if exec_result.get('status') == 'success':
            return exec_result.get('result')
        return {'success': False, 'error': exec_result.get('error')}
    return wrapped_tool


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

                    # Build auto-args map (dynamic, by name)
                    auto_args: Dict[str, Any] = {}
                    if artist_id is not None:
                        auto_args['artist_id'] = artist_id

                    for param_name, param in sig.parameters.items():
                        # Hide any parameter that will be auto-injected
                        if param_name in auto_args:
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

    async def execute_tool(self, persona_id: int, tool_name: str, args: Dict[str, Any] | None = None,
                           chat_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Execute a persona-scoped tool by name with provided args.

        The callable may be a partial; args are passed through without mutation.
        """
        self._logger.info(f"🔧 execute_tool called with tool_name: {tool_name}, args: {args}, persona_id: {persona_id}")
        tool_map = await self.build_persona_tool_map(persona_id)
        func = tool_map.get(tool_name)
        if not callable(func):
            self._logger.error(f"🔧 Tool not found or not callable: {tool_name}")
            return {'status': 'error', 'error': 'Tool not allowed or not found'}

        # Build auto-args map (dynamic, by name) for this persona
        auto_args: Dict[str, Any] = {}
        async with AsyncSessionLocal() as db_session:
            persona_result = await db_session.execute(
                select(Persona).where(Persona.id == persona_id)
            )
            persona = persona_result.scalar_one_or_none()
            artist_id = getattr(persona, 'artist_id', None) if persona else None
            if artist_id is not None:
                auto_args['artist_id'] = artist_id

        # Only inject auto-args that the function actually accepts
        try:
            sig = inspect.signature(func)
            accepted_param_names = set(sig.parameters.keys())
        except Exception:
            accepted_param_names = set()

        filtered_auto_args = {k: v for k, v in auto_args.items() if k in accepted_param_names}

        # System-provided values take precedence over user-provided ones
        effective_args = dict(args or {})
        effective_args.update(filtered_auto_args)
        self._logger.info(f"🔧 Final effective_args for tool {tool_name}: {effective_args}")

        try:
            if inspect.iscoroutinefunction(func):
                self._logger.info(f"🔧 Calling async tool {tool_name} with args: {effective_args}")
                result = await func(**effective_args) if effective_args else await func()
            else:
                self._logger.info(f"🔧 Calling sync tool {tool_name} with args: {effective_args}")
                result = func(**effective_args) if effective_args else func()
            self._logger.info(f"🔧 Tool {tool_name} returned: {result}")
            return {'status': 'success', 'result': result}
        except Exception as exc:  # noqa: BLE001
            return {'status': 'error', 'error': str(exc)}

    async def create_internal_langchain_tools(
            self,
            persona_id: int,
            available_tools_info: List[Dict[str, Any]]
    ) -> List[StructuredTool]:
        persona_tools = await self.build_persona_tool_map(persona_id)
        langchain_tools = []
        for tool_name, tool_func in persona_tools.items():
            tool_info = next((t for t in available_tools_info if t['name'] == tool_name), None)
            description = tool_info.get('description', f'Execute {tool_name}') if tool_info else f'Execute {tool_name}'
            if tool_info and 'parameters' in tool_info:
                try:
                    schema_fields = {}
                    annotations = {}
                    for param in tool_info['parameters']:
                        param_name = param['name']
                        param_type = param['type']
                        param_required = param['required']
                        param_default = param['default']
                        field_type = _get_field_type(param_type)
                        if param_required:
                            schema_fields[param_name] = Field(description=f"Parameter: {param_name}")
                            annotations[param_name] = field_type
                        else:
                            schema_fields[param_name] = Field(default=param_default, description=f"Parameter: {param_name}")
                            annotations[param_name] = Optional[field_type]
                    ToolSchema = type(f'{tool_name}Schema', (BaseModel,), {
                        '__annotations__': annotations,
                        **schema_fields
                    })
                    wrapped_tool = make_agent_tool_wrapper(self, persona_id, tool_name)
                    langchain_tool = StructuredTool.from_function(
                        coroutine=wrapped_tool,
                        name=tool_name,
                        description=description,
                        args_schema=ToolSchema
                    )
                except Exception:
                    continue
            else:
                ToolSchema = type(f'{tool_name}Schema', (BaseModel,), {})
                wrapped_tool = make_agent_tool_wrapper(self, persona_id, tool_name)
                langchain_tool = StructuredTool.from_function(
                    coroutine=wrapped_tool,
                    name=tool_name,
                    description=description,
                    args_schema=ToolSchema
                )
            langchain_tools.append(langchain_tool)
        return langchain_tools

    async def create_external_langchain_tools(self, persona_id: int) -> List[StructuredTool]:
        langchain_tools = []
        async with AsyncSessionLocal() as db_session:
            stmt = select(PersonaMCPServer).options(
                joinedload(PersonaMCPServer.mcp_server)
            ).where(PersonaMCPServer.persona_id == persona_id, PersonaMCPServer.is_active)
            result = await db_session.execute(stmt)
            external_servers = result.scalars().all()
        for server_link in external_servers:
            server = server_link.mcp_server
            server_config = {
                "command": server.command,
                "args": server.args_json or [],
                "env": server.env_json or {},
                "transport": "stdio"
            }
            client = MultiServerMCPClient({f"server_{server.id}": server_config})
            try:
                external_tools = await client.get_tools()
                for tool in external_tools:
                    annotations = {}
                    schema_fields = {}
                    if getattr(tool, 'inputSchema', None) and 'properties' in tool.inputSchema:
                        schema = tool.inputSchema
                        for param_name, param_schema in schema['properties'].items():
                            field_type = _get_field_type(param_schema.get('type', 'string'))
                            if param_name in schema.get('required', []):
                                schema_fields[param_name] = Field(description=f"Parameter: {param_name}")
                                annotations[param_name] = field_type
                            else:
                                schema_fields[param_name] = Field(default=param_schema.get('default'), description=f"Parameter: {param_name}")
                                annotations[param_name] = Optional[field_type]
                    ToolSchema = type(f"{server.name}:{tool.name}Schema", (BaseModel,), {
                        '__annotations__': annotations,
                        **schema_fields
                    })
                    tool_qname = f"{server.name}:{tool.name}"
                    async def external_wrapper(**kwargs):
                        return await call_mcp_tool_by_server_id(server.id, tool.name, kwargs or {})
                    langchain_tool = StructuredTool.from_function(
                        coroutine=external_wrapper,
                        name=tool_qname,
                        description=(tool.description or ''),
                        args_schema=ToolSchema
                    )
                    langchain_tools.append(langchain_tool)
            except Exception as e:
                self._logger.error(f"Failed to load tools from MCP server {server.name}: {e}")
        return langchain_tools

    async def create_langchain_tools(
            self,
            persona_id: int,
            available_tools_info: List[Dict[str, Any]]
    ) -> List[StructuredTool]:
        internal_tools = await self.create_internal_langchain_tools(persona_id, available_tools_info)
        external_tools = await self.create_external_langchain_tools(persona_id)
        return internal_tools + external_tools
