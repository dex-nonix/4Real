"""
Tools module for LLM tool management with dynamic loading and framework adapters.

This module provides a complete tool management system supporting:
- Dynamic tool references with lazy loading
- Universal pattern recognition 
- Framework adapters for LangChain, MCP, OpenAI
- Context-aware property resolution
- Change detection and reloading
"""

from .decorators import (
    llm_tool, 
    NX_LLM_TOOL_ATTRIBUTE,
    is_llm_tool,
    get_llm_tool_info,
    extract_tool_metadata
)

from .tools_manager import NxLLMToolsManager



from .utils import resolve_safe_path

__all__ = [
    # Main manager
    "NxLLMToolsManager",
    
    # Decorators and helpers
    "llm_tool",
    "NX_LLM_TOOL_ATTRIBUTE", 
    "is_llm_tool",
    "get_llm_tool_info",
    "extract_tool_metadata",
    
    # Tool references
    # Utilities
    "resolve_safe_path"
]
