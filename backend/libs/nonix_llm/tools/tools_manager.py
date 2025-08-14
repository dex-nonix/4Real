"""
Tools manager for loading and managing LLM tools with dynamic references.

This module provides the complete redesigned NxLLMToolsManager with:
- Dynamic tool reference system
- Lazy loading with change detection  
- Universal pattern recognition
- Context-aware tool resolution
- Generic tool container support
- Integration with existing decorator and security systems
- Framework adapters for LangChain, MCP, and OpenAI
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import inspect

from .tool_references.base import ToolReference
from .tool_references.module_function import ModuleFunctionReference
from .tool_references.module_reference import ModuleReference
from .tool_references.file_reference import FileReference
from .tool_references.folder_reference import FolderReference
from .tool_references.config_dict_reference import ConfigDictReference
from .tool_references.nested_manager_reference import NestedManagerReference
from .tool_references.object_reference import ObjectReference
from .tool_references.lang_chain_reference import LangChainToolReference
from .tool_references.mcp_client_reference import MCPClientReference


class NxLLMToolsManager:
    """
    Manager for loading and organizing LLM tools from various sources with dynamic references.
    
    Supports:
    - String patterns: "module:function", "module", "./path", "/path"
    - Dictionary configs: {"func": "..."}, {"file": "..."}, {"folder": "..."}
    - LangChain tools: {"langchain_tool": tool_instance}
    - MCP clients: {"mcp_client": {"server": "...", "command": "..."}}
    - Object instances: functions, class instances, other managers
    - Lazy loading with file system change detection
    - Context-aware property resolution and partial binding
    - Full compatibility with existing @llm_tool decorator system
    - Framework adapters for LangChain, MCP, OpenAI, Anthropic
    """

    def __init__(self, tools: Optional[List[Any]] = None):
        """
        Initialize the tools manager with optional initial tools.
        
        Args:
            tools: Optional list of tool sources to register initially
        """
        self._tool_references: List[ToolReference] = []

        if tools:
            for tool in tools:
                self.register(tool)

    def register(self, tool_source: Any, base_dir: Optional[Path] = None) -> None:
        """
        Register a tool source for dynamic loading.
        
        Args:
            tool_source: Any supported tool source type
            base_dir: Base directory for resolving relative paths
        """
        reference = self._create_reference(tool_source, base_dir)
        self._tool_references.append(reference)

    def get_all_tools(self, context: Optional[Dict[str, Any]] = None,
                      partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all tools from all references with change detection.
        
        This method integrates with existing property override and context systems.
        
        Args:
            context: Runtime context for property resolution (compatible with existing context usage)
            partial_map: Map for partial binding injection (compatible with existing partial system)
            
        Returns:
            List of tool containers with all metadata, fully compatible with existing LLM frameworks
        """
        all_tools = []

        for reference in self._tool_references:
            try:
                tools = reference.get_tools(context, partial_map)

                # Apply additional validation and compatibility processing
                for tool in tools:
                    # Ensure compatibility with existing tool validation
                    validated_tool = self._validate_and_enhance_tool(tool, context)
                    if validated_tool:
                        all_tools.append(validated_tool)

            except Exception as e:
                # Log error but continue with other references
                print(f"Error loading tools from reference {reference.source}: {str(e)}")

        return all_tools

    def get_langchain_tools(self, context: Optional[Dict[str, Any]] = None,
                            partial_map: Optional[Dict[str, Any]] = None) -> List:
        """
        Get tools in LangChain Tool format.
        
        Args:
            context: Runtime context for property resolution
            partial_map: Map for partial binding injection
            
        Returns:
            List of LangChain Tool instances
        """
        universal_tools = self.get_all_tools(context, partial_map)
        langchain_tools = []

        for tool in universal_tools:
            try:
                langchain_tool = self._convert_to_langchain_tool(tool)
                if langchain_tool:
                    langchain_tools.append(langchain_tool)
            except Exception as e:
                print(f"Error converting tool {tool['name']} to LangChain format: {str(e)}")

        return langchain_tools

    def get_mcp_tools(self, context: Optional[Dict[str, Any]] = None,
                      partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get tools in MCP format.
        
        Args:
            context: Runtime context for property resolution
            partial_map: Map for partial binding injection
            
        Returns:
            List of MCP-compatible tool dictionaries
        """
        universal_tools = self.get_all_tools(context, partial_map)
        mcp_tools = []

        for tool in universal_tools:
            try:
                mcp_tool = self._convert_to_mcp_tool(tool)
                if mcp_tool:
                    mcp_tools.append(mcp_tool)
            except Exception as e:
                print(f"Error converting tool {tool['name']} to MCP format: {str(e)}")

        return mcp_tools

    def get_openai_tools(self, context: Optional[Dict[str, Any]] = None,
                         partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get tools in OpenAI function calling format.
        
        Args:
            context: Runtime context for property resolution
            partial_map: Map for partial binding injection
            
        Returns:
            List of OpenAI function calling dictionaries
        """
        universal_tools = self.get_all_tools(context, partial_map)
        openai_tools = []

        for tool in universal_tools:
            try:
                openai_tool = self._convert_to_openai_tool(tool)
                if openai_tool:
                    openai_tools.append(openai_tool)
            except Exception as e:
                print(f"Error converting tool {tool['name']} to OpenAI format: {str(e)}")

        return openai_tools

    def disable_tool(self, tool_name: str) -> bool:
        """
        Disable a tool by name.
        
        Args:
            tool_name: Name of the tool to disable
            
        Returns:
            True if tool was found and disabled, False otherwise
        """
        for reference in self._tool_references:
            if reference.cached_tools:
                for tool in reference.cached_tools:
                    if tool["name"] == tool_name:
                        reference.disabled = True
                        return True
        return False

    def enable_tool(self, tool_name: str) -> bool:
        """
        Enable a tool by name.
        
        Args:
            tool_name: Name of the tool to enable
            
        Returns:
            True if tool was found and enabled, False otherwise
        """
        for reference in self._tool_references:
            if reference.cached_tools:
                for tool in reference.cached_tools:
                    if tool["name"] == tool_name:
                        reference.disabled = False
                        return True
        return False

    def _create_reference(self, tool_source: Any, base_dir: Optional[Path] = None) -> ToolReference:
        """
        Enhanced pattern detection supporting all tool types including universal disabled flag.
        
        Args:
            tool_source: Tool source of any supported type
            base_dir: Base directory for resolving relative paths
            
        Returns:
            Appropriate ToolReference instance
        """
        # Handle universal disabled flag first
        disabled = False
        clean_source = tool_source

        if isinstance(tool_source, dict) and "disabled" in tool_source:
            disabled = tool_source["disabled"]
            clean_source = {k: v for k, v in tool_source.items() if k != "disabled"}

        # Create reference based on clean source
        reference = None

        # String patterns
        if isinstance(clean_source, str):
            if ":" in clean_source:
                # Module:function pattern
                reference = ModuleFunctionReference(clean_source)
            elif clean_source.startswith(("./", "/")):
                # Path patterns
                path = Path(clean_source)
                if base_dir and not path.is_absolute():
                    path = base_dir / path

                if path.is_file():
                    reference = FileReference(str(path))
                elif path.is_dir():
                    reference = FolderReference(str(path))
                else:
                    # Assume it's a module import
                    reference = ModuleReference(clean_source)
            else:
                # Assume it's a module import
                reference = ModuleReference(clean_source)

        # Dictionary patterns
        elif isinstance(clean_source, dict):
            # NEW: LangChain tool support
            if "langchain_tool" in clean_source:
                reference = LangChainToolReference(clean_source)

            # NEW: MCP client support
            elif "mcp_client" in clean_source:
                reference = MCPClientReference(clean_source)

            # Existing dict patterns
            elif "func" in clean_source:
                reference = ConfigDictReference(clean_source)
            elif "file" in clean_source:
                file_path = clean_source["file"]
                if base_dir and not Path(file_path).is_absolute():
                    file_path = str(base_dir / file_path)
                reference = FileReference(file_path)
            elif "folder" in clean_source:
                folder_path = clean_source["folder"]
                if base_dir and not Path(folder_path).is_absolute():
                    folder_path = str(base_dir / folder_path)
                reference = FolderReference(folder_path)
            else:
                raise ValueError(f"Unsupported dictionary pattern: {list(clean_source.keys())}")

        # Direct object instances
        else:
            # NEW: Direct LangChain tool instances
            if hasattr(clean_source, 'name') and hasattr(clean_source, 'func'):
                reference = LangChainToolReference(clean_source)

            # NEW: Direct MCP client instances
            elif hasattr(clean_source, 'get_tools') and hasattr(clean_source, 'servers'):
                reference = MCPClientReference(clean_source)

            # Nested manager instances
            elif hasattr(clean_source, 'get_all_tools') and hasattr(clean_source, '_tool_references'):
                reference = NestedManagerReference(clean_source)

            # Generic object reference
            else:
                reference = ObjectReference(clean_source)

        if reference is None:
            raise ValueError(f"Unsupported tool source type: {type(tool_source)}")

        # Set disabled state on ANY reference type
        reference.disabled = disabled

        return reference

    def _validate_and_enhance_tool(self, tool: Dict[str, Any],
                                   context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Validate and enhance tool for compatibility with existing systems.
        
        Args:
            tool: Tool container to validate
            context: Runtime context
            
        Returns:
            Enhanced and validated tool container, or None if invalid
        """
        # Basic validation
        if not all(key in tool for key in ["name", "description", "function"]):
            return None

        # Apply context enhancements for compatibility
        if context:
            tool = self._apply_context_enhancements(tool, context)

        return tool

    def _apply_context_enhancements(self, tool: Dict[str, Any],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply additional context-based enhancements for compatibility.
        
        Args:
            tool: Tool container
            context: Runtime context
            
        Returns:
            Enhanced tool container
        """
        enhanced_tool = tool.copy()

        # Support legacy context key patterns
        if "root_path" in context and "root_path" not in enhanced_tool["props"]:
            # Auto-inject root_path for file tools that might need it
            if any(keyword in tool["name"].lower() for keyword in ["file", "read", "write", "path"]):
                enhanced_tool["props"]["root_path"] = context["root_path"]
                if "root_path" not in enhanced_tool["hidden_props"]:
                    enhanced_tool["hidden_props"].append("root_path")

        # Support other common context patterns used in existing code
        for context_key in ["output_dir", "work_dir", "base_path"]:
            if context_key in context and context_key not in enhanced_tool["props"]:
                # Only inject if tool might use this context
                if context_key.replace("_", "").lower() in str(enhanced_tool.get("param_descriptions", {})).lower():
                    enhanced_tool["props"][context_key] = context[context_key]

        return enhanced_tool

    def _convert_to_langchain_tool(self, tool: Dict[str, Any]):
        """
        Convert universal tool container to LangChain Tool.
        
        Args:
            tool: Universal tool container
            
        Returns:
            LangChain Tool instance
        """
        try:
            from langchain_core.tools import Tool
            from pydantic import create_model, Field
            from typing import Optional, Any

            # Check if this was originally a LangChain tool
            if tool["metadata"].get("original_tool") and tool["metadata"]["source_type"] == "langchaintool":
                return tool["metadata"]["original_tool"]

            # Create args_schema from param_descriptions with proper optional handling
            args_schema = None
            if tool["param_descriptions"]:
                # Use the ACTUAL function (which may be partial) instead of unwrapping it
                func = tool["function"]
                
                # Get the signature of the current function (partial or original)
                sig = inspect.signature(func)
                fields = {}
                
                for param_name, param_desc in tool["param_descriptions"].items():
                    # Skip hidden props and partial args
                    if param_name in tool.get("hidden_props", []):
                        print(f"  - SKIPPING {param_name} (in hidden_props)")
                        continue
                    if param_name in tool.get("partial", []):
                        print(f"  - SKIPPING {param_name} (in partial)")
                        continue
                    
                    # Check if parameter exists in the CURRENT function signature
                    if param_name not in sig.parameters:
                        print(f"  - SKIPPING {param_name} (not in current function signature)")
                        continue
                    
                    # Check if parameter has a default value in the function signature
                    param_info = sig.parameters.get(param_name)
                    if param_info and param_info.default != inspect.Parameter.empty:
                        # Optional parameter with default
                        # print(f"  - OPTIONAL {param_name} (has default: {param_info.default})")
                        fields[param_name] = (Optional[str], Field(default=None, description=param_desc))
                    else:
                        # Required parameter
                        # print(f"  - REQUIRED {param_name} (no default)")
                        fields[param_name] = (str, Field(description=param_desc))

                print(f"  - Final fields: {list(fields.keys())}")
                
                if fields:
                    args_schema = create_model(f"{tool['name']}_Args", **fields)

            # Create LangChain Tool
            langchain_tool = Tool(
                name=tool["name"],
                description=tool["description"],
                func=tool["function"],
                args_schema=args_schema
            )

            return langchain_tool

        except ImportError:
            print("LangChain not installed. Cannot convert to LangChain Tool format.")
            return None
        except Exception as e:
            print(f"Error creating LangChain Tool: {str(e)}")
            return None

    def _convert_to_mcp_tool(self, tool: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert universal tool container to MCP format.
        
        Args:
            tool: Universal tool container
            
        Returns:
            MCP-compatible tool dictionary
        """
        try:
            # Check if this was originally an MCP tool
            if tool["metadata"].get("original_tool") and tool["metadata"]["source_type"] == "mcpclient":
                # Return original MCP tool format if available
                return tool["metadata"]["original_tool"]

            # Create MCP-compatible format
            mcp_tool = {
                "name": tool["name"],
                "description": tool["description"],
                "function": tool["function"],
                "parameters": tool["param_descriptions"]
            }

            return mcp_tool

        except Exception as e:
            print(f"Error creating MCP tool: {str(e)}")
            return None

    def _convert_to_openai_tool(self, tool: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert universal tool container to OpenAI function calling format.
        
        Args:
            tool: Universal tool container
            
        Returns:
            OpenAI function calling dictionary
        """
        try:
            # Create OpenAI function schema
            function_schema = {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }

            # Convert param_descriptions to JSON schema properties
            for param_name, param_desc in tool["param_descriptions"].items():
                function_schema["parameters"]["properties"][param_name] = {
                    "type": "string",  # Default to string type
                    "description": param_desc
                }

            # Create OpenAI tool format
            openai_tool = {
                "type": "function",
                "function": function_schema
            }

            return openai_tool

        except Exception as e:
            print(f"Error creating OpenAI tool: {str(e)}")
            return None

    # Legacy compatibility methods
    def load_tools_from_config(self, config: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[
        Dict[str, Any]]:
        """
        Legacy compatibility method for loading tools from configuration.
        
        Args:
            config: List of tool configurations
            context: Runtime context
            
        Returns:
            List of universal tool containers
        """
        for tool_config in config:
            self.register(tool_config)

        return self.get_all_tools(context)

    def extract_decorated_tools(self, obj: Any, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Legacy compatibility method for extracting decorated tools.
        
        Args:
            obj: Object to extract tools from
            context: Runtime context
            
        Returns:
            List of universal tool containers
        """
        self.register(obj)
        return self.get_all_tools(context)
