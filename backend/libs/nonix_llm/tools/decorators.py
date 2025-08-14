"""
Decorators for LLM tools.

This module provides decorators for marking functions and methods as LLM tools.
"""

from typing import Dict, Any, List, Callable, Optional

# Attribute name used to mark functions as LLM tools
NX_LLM_TOOL_ATTRIBUTE = "__nx_llm_tool__"


def llm_tool(description: str = None,
             partial: List[str] = None,
             props: Dict[str, Any] = None,
             hidden_props: List[str] = None,
             param_descriptions: Dict[str, str] = None,
             name: str = None):
    """
    Decorator to mark a function or method as an LLM tool.
    
    Args:
        description: Tool description for the LLM
        partial: List of arguments to bind (e.g., ["context", "config"])
        props: Dictionary of predefined properties
        hidden_props: List of property names to hide from the LLM
        param_descriptions: Dictionary of parameter descriptions for the LLM
        name: Custom tool name (defaults to function name)
        
    Returns:
        Decorated function with LLM tool metadata
    """

    def decorator(func: Callable) -> Callable:
        # Store tool metadata on the function
        tool_info = {
            "name": name or func.__name__,
            "description": description or func.__doc__ or f"Function {func.__name__}",
            "partial": partial or [],
            "props": props or {},
            "hidden_props": hidden_props or [],
            "param_descriptions": param_descriptions or {}
        }

        # Set the attribute on the function directly
        setattr(func, NX_LLM_TOOL_ATTRIBUTE, tool_info)

        # Return the original function without wrapping
        return func

    return decorator


def is_llm_tool(func: Callable) -> bool:
    """
    Check if a function/method is decorated with @llm_tool.
    
    Args:
        func: Function or method to check
        
    Returns:
        True if the function is an LLM tool, False otherwise
    """
    return hasattr(func, NX_LLM_TOOL_ATTRIBUTE)


def get_llm_tool_info(func: Callable) -> Optional[Dict[str, Any]]:
    """
    Extract LLM tool metadata from a decorated function.
    
    Args:
        func: Function or method to extract metadata from
        
    Returns:
        Tool metadata dictionary if decorated, None otherwise
    """
    if not is_llm_tool(func):
        return None
    
    return getattr(func, NX_LLM_TOOL_ATTRIBUTE)


def extract_tool_metadata(func: Callable, config_overrides: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Extract complete tool metadata with optional config overrides.
    
    Args:
        func: Function or method to extract metadata from
        config_overrides: Optional configuration overrides
        
    Returns:
        Complete tool metadata dictionary or None if not a tool
    """
    if not is_llm_tool(func):
        # Return metadata for non-decorated functions if config overrides provided
        if config_overrides:
            return {
                "name": config_overrides.get("name", func.__name__),
                "description": config_overrides.get("description", func.__doc__ or f"Function {func.__name__}"),
                "props": config_overrides.get("props", {}),
                "hidden_props": config_overrides.get("hidden_props", []),
                "param_descriptions": config_overrides.get("param_descriptions", {}),
                "partial": config_overrides.get("partial", [])
            }
        return None
    
    # Get tool info from decorator
    tool_info = get_llm_tool_info(func)
    
    # Apply config overrides if provided
    if config_overrides:
        metadata = {
            "name": config_overrides.get("name", tool_info.get("name", func.__name__)),
            "description": config_overrides.get("description", tool_info.get("description", func.__doc__ or f"Function {func.__name__}")),
            "props": {**tool_info.get("props", {}), **config_overrides.get("props", {})},
            "hidden_props": config_overrides.get("hidden_props", tool_info.get("hidden_props", [])),
            "param_descriptions": {**tool_info.get("param_descriptions", {}), **config_overrides.get("param_descriptions", {})},
            "partial": config_overrides.get("partial", tool_info.get("partial", []))
        }
    else:
        metadata = {
            "name": tool_info.get("name", func.__name__),
            "description": tool_info.get("description", func.__doc__ or f"Function {func.__name__}"),
            "props": tool_info.get("props", {}),
            "hidden_props": tool_info.get("hidden_props", []),
            "param_descriptions": tool_info.get("param_descriptions", {}),
            "partial": tool_info.get("partial", [])
        }
    
    return metadata
