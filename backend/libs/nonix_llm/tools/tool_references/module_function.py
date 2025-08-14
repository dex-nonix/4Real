from importlib import import_module
from typing import Optional, Dict, Any, List

import time

from .base import ToolReference
from .. import extract_tool_metadata


class ModuleFunctionReference(ToolReference):
    """Reference to a specific function in a module."""

    def __init__(self, source: str, config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)

        if ":" not in source:
            raise ValueError(f"ModuleFunctionReference requires 'module:function' format, got: {source}")

        self.module_path, self.symbol_name = source.split(":", 1)
        self.module = None
        self.function = None

    def needs_reload(self) -> bool:
        """Module functions don't change at runtime."""
        return self.cached_tools is None

    def reload(self) -> None:
        """Load the function from the module."""
        try:
            self.module = import_module(self.module_path)
            self.function = getattr(self.module, self.symbol_name)

            # Extract tool metadata using helper function
            metadata = extract_tool_metadata(self.function, self.config_overrides)

            if metadata:
                tool = self._create_tool_container(
                    name=metadata["name"],
                    description=metadata["description"],
                    function=self.function,
                    props=metadata["props"],
                    hidden_props=metadata["hidden_props"],
                    param_descriptions=metadata["param_descriptions"],
                    partial=metadata["partial"]
                )

                self.cached_tools = [tool]
            else:
                self.cached_tools = []

            self.last_load_time = time.time()
            self.error_state = None

        except (ImportError, AttributeError) as e:
            self.error_state = f"Failed to import {self.source}: {str(e)}"
            self.cached_tools = []

    def get_tools(self, context: Optional[Dict[str, Any]] = None,
                  partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get the function as a tool with context and partials applied."""
        if self.disabled:
            return []

        if self.needs_reload():
            self.reload()

        if self.error_state:
            return []

        return [self._apply_context_and_partials(tool, context, partial_map)
                for tool in self.cached_tools]
