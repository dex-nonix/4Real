import time
from typing import Union, Dict, Any, Optional, List

from .base import ToolReference


class LangChainToolReference(ToolReference):
    """Reference to LangChain Tool instances."""

    def __init__(self, source: Union[Dict[str, Any], Any], config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)

        if isinstance(source, dict) and "langchain_tool" in source:
            self.tool = source["langchain_tool"]
        else:
            self.tool = source

    def needs_reload(self) -> bool:
        """LangChain tools are static."""
        return self.cached_tools is None

    def get_tools(self, context: Optional[Dict[str, Any]] = None,
                  partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tools from this reference with context and partial injection."""
        if self.disabled:
            return []  # Skip disabled tools

        if self.needs_reload():
            self.reload()

        if self.error_state:
            return []

        return [self._apply_context_and_partials(tool, context, partial_map)
                for tool in self.cached_tools or []]

    def reload(self) -> None:
        """Convert LangChain Tool to universal container."""
        try:
            # Extract metadata from LangChain Tool
            name = getattr(self.tool, 'name', 'unknown_tool')
            description = getattr(self.tool, 'description', 'No description available')
            func = getattr(self.tool, 'func', None)
            args_schema = getattr(self.tool, 'args_schema', None)

            if not func:
                self.error_state = "LangChain tool missing func attribute"
                self.cached_tools = []
                return

            # Extract parameter descriptions from args_schema if available
            param_descriptions = {}
            if args_schema and hasattr(args_schema, '__fields__'):
                for field_name, field_info in args_schema.__fields__.items():
                    if hasattr(field_info, 'description') and field_info.description:
                        param_descriptions[field_name] = field_info.description

            # Create universal container
            tool = self._create_tool_container(
                name=name,
                description=description,
                function=func,
                param_descriptions=param_descriptions
            )

            # Store original LangChain tool in metadata
            tool["metadata"]["original_tool"] = self.tool
            tool["metadata"]["framework_specific"]["langchain"] = {
                "args_schema": args_schema
            }

            self.cached_tools = [tool]
            self.last_load_time = time.time()
            self.error_state = None

        except Exception as e:
            self.error_state = f"Failed to convert LangChain tool: {str(e)}"
            self.cached_tools = []
