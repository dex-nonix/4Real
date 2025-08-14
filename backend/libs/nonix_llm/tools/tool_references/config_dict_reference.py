import time
from importlib import import_module
from typing import Dict, Any, Optional, List

from .base import ToolReference
from .. import extract_tool_metadata


class ConfigDictReference(ToolReference):
    """Reference to a tool defined by a configuration dictionary."""

    def __init__(self, source: Dict[str, Any], config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)
        self.config = source

    def needs_reload(self) -> bool:
        """Config dicts are static."""
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
        """Load tool from configuration dictionary."""
        try:
            func_spec = self.config["func"]
            if ":" not in func_spec:
                self.error_state = f"Invalid func format: {func_spec}"
                self.cached_tools = []
                return

            module_path, symbol_name = func_spec.split(":", 1)
            module = import_module(module_path)
            function = getattr(module, symbol_name)

            # Apply config overrides
            merged_config = {**self.config, **self.config_overrides}
            metadata = extract_tool_metadata(function, merged_config)

            if metadata:
                tool = self._create_tool_container(
                    name=metadata["name"],
                    description=metadata["description"],
                    function=function,
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

        except (ImportError, AttributeError, KeyError) as e:
            self.error_state = f"Failed to load tool from config: {str(e)}"
            self.cached_tools = []
