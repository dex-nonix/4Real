from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator

from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from .tool_runtime import build_persona_tool_map
from ..services.chat_service.streaming_interface import StreamingChunk
from ..utils.llm_message_utils import iter_messages, LCAIMessage, LCToolMessage

# Get logger for this module
logger = logging.getLogger(__name__)


async def create_langchain_tools(persona_id: int, available_tools_info: List[Dict[str, Any]]) -> List[StructuredTool]:
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
    persona_tools = build_persona_tool_map(persona_id)

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
                        schema_fields[param_name] = Field(default=param_default, description=f"Parameter: {param_name}")
                        annotations[param_name] = Optional[field_type]

                # Create the schema class dynamically with proper annotations
                ToolSchema = type(f'{tool_name}Schema', (BaseModel,), {
                    '__annotations__': annotations,
                    **schema_fields
                })

                # Create StructuredTool with proper Pydantic schema
                langchain_tool = StructuredTool.from_function(
                    func=tool_func,  # Use the partial directly
                    name=tool_name,
                    description=description,
                    args_schema=ToolSchema
                )

                logger.debug(f"🔧 Created tool '{tool_name}' with Pydantic schema")

            except Exception as e:
                logger.warning(f"🔧 Failed to create Pydantic schema for tool '{tool_name}': {e}", exc_info=True)
                # Fallback: create tool without schema
                langchain_tool = StructuredTool.from_function(
                    func=tool_func,
                    name=tool_name,
                    description=description
                )
        else:
            # Fallback: no schema, just basic tool
            langchain_tool = StructuredTool.from_function(
                func=tool_func,
                name=tool_name,
                description=description
            )

        langchain_tools.append(langchain_tool)

    logger.info(f"🔧 Created {len(langchain_tools)} LangChain tools for persona {persona_id}")
    return langchain_tools


async def run_chat_streaming(provider: Any, mapping: Any,
                             messages: List[Dict[str, Any]],
                             available_tools_info: List[Dict[str, Any]],
                             persona_id: int) -> AsyncGenerator[StreamingChunk, None]:
    """Streaming version of run_chat using llm_message_utils.
    
    This function ONLY handles persona-based clients with tools.
    persona_id is MANDATORY - no checks needed.
    """
    cfg: Dict[str, Any] = provider.config_json or {}
    model_name: str = mapping.model_name
    params: Dict[str, Any] = mapping.parameters_json or {}

    module_name: str = getattr(provider, 'module', '') or ''
    class_name: str = getattr(provider, 'cls', '') or ''
    method_name: str = (getattr(provider, 'method', None) or 'invoke')

    if not module_name or not class_name:
        # Fallback: echo last user
        last_user = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
        text = (last_user or {}).get('content', '')
        if isinstance(text, dict):
            text = text.get('text', str(text))
        yield StreamingChunk(content=f"Provider not configured (module/class missing). Echo: {text}",
                             chunk_type="complete", is_final=True)
        return

    # Build kwargs: provider creds/connection + model + mapping params (mapping overrides)
    kwargs: Dict[str, Any] = {}
    kwargs.update(cfg or {})
    # Standardize model kw for LangChain chat clients
    kwargs['model'] = model_name
    kwargs.update(params or {})

    try:
        module = importlib.import_module(module_name)
        client_cls = getattr(module, class_name)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Provider import error: {exc}", exc_info=True)
        yield StreamingChunk(content=f'Provider import error: {exc}',
                             chunk_type="complete", is_final=True)
        return

    try:
        client = client_cls(**kwargs)

        # Create LangChain tools (can be empty list if no tools)
        langchain_tools = []
        if available_tools_info is not None:
            langchain_tools = create_langchain_tools(persona_id, available_tools_info)
            logger.info(f"🔧 Created {len(langchain_tools)} LangChain tools for persona {persona_id}")

        # Get the persona for system prompt
        from ..models.persona import Persona
        persona = Persona.query.filter_by(id=persona_id).first()
        persona_system_prompt = persona.system_prompt if persona else ""

        # Create the ChatPromptTemplate with persona system prompt
        if persona_system_prompt:
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", persona_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
        else:
            # No system prompt - just chat history and input
            chat_prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])

        # Create the ReAct agent (no prompt needed)
        agent = create_react_agent(
            client,
            langchain_tools
        )

        logger.info(f"🔧 Created ReAct agent with {len(langchain_tools)} tools")

        # Chain the prompt with the agent
        new_agent = chat_prompt | agent

        # Get the last user message
        last_user_msg = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
        if last_user_msg:
            user_content = last_user_msg.get('content', '')
            if isinstance(user_content, dict):
                user_content = user_content.get('text', str(user_content))

            # Convert messages to string for agent
            conversation_history = []
            for m in messages:
                role = m.get('role')
                content = m.get('content')
                if isinstance(content, dict):
                    content = content.get('text', str(content))
                if role == 'user':
                    conversation_history.append(f"Human: {content}")
                elif role == 'assistant':
                    conversation_history.append(f"Assistant: {content}")
                elif role == 'system':
                    conversation_history.append(f"System: {content}")

            # Use streaming with astream_events

            async for mode, message in iter_messages(new_agent.astream_events({
                "chat_history": conversation_history,
                "input": user_content
            })):
                if mode == "start":
                    if isinstance(message, LCAIMessage):
                        yield StreamingChunk(content="", chunk_type="ai_start")
                    elif isinstance(message, LCToolMessage):
                        yield StreamingChunk(content="", chunk_type="tool_start",
                                             metadata={"tool_name": message.status.get("tool_name", "unknown")})

                elif mode == "update":
                    if isinstance(message, LCAIMessage):
                        yield StreamingChunk(content=message.status.get("content", ""), chunk_type="text")

                elif mode == "end":
                    if isinstance(message, LCAIMessage):
                        yield StreamingChunk(content="", chunk_type="complete", is_final=True)
                    elif isinstance(message, LCToolMessage):
                        yield StreamingChunk(content="", chunk_type="tool_end",
                                             metadata={"tool_name": message.status.get("tool_name", "unknown")})

        else:
            yield StreamingChunk(content="No user message found", chunk_type="complete", is_final=True)

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Provider error: {exc}", exc_info=True)
        yield StreamingChunk(content=f'Provider error: {exc}', chunk_type="complete", is_final=True)
