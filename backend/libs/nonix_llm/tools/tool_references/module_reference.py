from importlib import import_module
from inspect import getmembers, isfunction, ismethod
from typing import Optional, Dict, Any, List

import time

from .base import ToolReference
from .. import extract_tool_metadata, is_llm_tool


class ModuleReference(ToolReference):
    """Reference to all decorated functions in a module."""

    def __init__(self, source: str, config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)
        self.module_path = source
        self.module = None

    def needs_reload(self) -> bool:
        """Module contents don't change at runtime."""
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
        """Load all decorated functions from the module."""
        try:
            self.module = import_module(self.module_path)

            tools = []
            for name, obj in getmembers(self.module):
                if (isfunction(obj) or ismethod(obj)) and is_llm_tool(obj):
                    metadata = extract_tool_metadata(obj, self.config_overrides)
                    if metadata:
                        tool = self._create_tool_container(
                            name=metadata["name"],
                            description=metadata["description"],
                            function=obj,
                            props=metadata["props"],
                            hidden_props=metadata["hidden_props"],
                            param_descriptions=metadata["param_descriptions"],
                            partial=metadata["partial"]
                        )
                        tools.append(tool)

            self.cached_tools = tools
            self.last_load_time = time.time()
            self.error_state = None

        except ImportError as e:
            self.error_state = f"Failed to import module {self.source}: {str(e)}"
            self.cached_tools = []
