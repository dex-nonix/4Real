from __future__ import annotations

from typing import Any, Dict, List, Optional
import importlib
import logging
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.tools import StructuredTool
from langchain.agents import create_react_agent
from .tool_runtime import build_persona_tool_map
from .internal_tool_registry import registry as internal_tool_registry
from pydantic import BaseModel, Field

# Get logger for this module
logger = logging.getLogger(__name__)


def create_langchain_tools(persona_id: int, available_tools_info: List[Dict[str, Any]]) -> List[StructuredTool]:
    """Create LangChain StructuredTool objects from persona tools with proper Pydantic schemas."""
    
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
                    field_type = _get_field_type(param_type)
                    
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


def run_chat(provider: Any, mapping: Any, messages: List[Dict[str, Any]], available_tools_info: List[Dict[str, Any]] = None, persona_id: int = None) -> Dict[str, Any]:
    """Provider adapter driven entirely by DB configuration (persona-selected mapping).

    - Imports provider.module, resolves provider.class
    - Instantiates with merged kwargs: provider.config_json + model + mapping.parameters_json
    - Calls provider.method (default 'invoke') with LangChain-formatted messages
    - Now includes available_tools_info for tool-aware LLMs
    - persona_id enables proper tool integration with partial binding
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
        return { 'type': 'text', 'text': f"Provider not configured (module/class missing). Echo: {text}" }

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
        return { 'type': 'text', 'text': f'Provider import error: {exc}' }

    try:
        client = client_cls(**kwargs)
        
        # If we have tools, create a LangChain agent
        if available_tools_info and persona_id:
            try:
                # Create LangChain tools using utility function
                langchain_tools = create_langchain_tools(persona_id, available_tools_info)
                
                logger.info(f"🔧 Created {len(langchain_tools)} LangChain tools for persona {persona_id}")
                
                # Create the ReAct agent with tools
                agent = create_react_agent(
                    client,
                    langchain_tools
                )
                
                logger.info(f"🔧 Created ReAct agent with {len(langchain_tools)} tools")
                
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
                
                # Get the last user message
                last_user_msg = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
                if last_user_msg:
                    user_content = last_user_msg.get('content', '')
                    if isinstance(user_content, dict):
                        user_content = user_content.get('text', str(user_content))
                    
                    # Run the agent
                    response = agent.invoke({
                        "input": user_content,
                        "chat_history": conversation_history
                    })
                    
                    # Extract response
                    if hasattr(response, 'output'):
                        text = response.output
                    else:
                        text = str(response)
                    
                    return { 'type': 'text', 'text': text }
                else:
                    return { 'type': 'text', 'text': 'No user message found' }
                    
            except ImportError as e:
                logger.warning(f"🔧 LangChain tools not available: {e}")
                # Fall back to basic client call
                pass
            except Exception as e:
                logger.error(f"🔧 Error creating LangChain agent: {e}", exc_info=True)
                # Fall back to basic client call
                pass
        
        # Fallback: use basic client method (no tools)
        method = getattr(client, method_name, None)
        if not callable(method):
            return { 'type': 'text', 'text': f"Provider method '{method_name}' not found on {class_name}" }
        
        # Convert to LC messages (simple text only)
        lc_messages = []
        
        # Add existing messages
        for m in messages:
            role = m.get('role')
            content = m.get('content')
            if isinstance(content, dict):
                content = content.get('text', str(content))
            if role == 'system':
                lc_messages.append(SystemMessage(content=content))
            elif role == 'assistant':
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        
        resp = method(lc_messages)
        text = getattr(resp, 'content', '') if hasattr(resp, 'content') else (resp or '')
        if isinstance(text, dict):
            # Normalize to text response
            text = text.get('text', str(text))
        return { 'type': 'text', 'text': text or '' }
        
    except Exception as exc:  # noqa: BLE001
        return { 'type': 'text', 'text': f'Provider error: {exc}' }


 


