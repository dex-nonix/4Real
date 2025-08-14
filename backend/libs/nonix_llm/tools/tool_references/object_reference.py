from typing import Any, Optional, Dict, List

import time

from .. import extract_tool_metadata
from .base import ToolReference


class ObjectReference(ToolReference):
    """Reference to a callable object (function, class instance, etc.)."""

    def __init__(self, source: Any, config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)
        self.obj = source

    def needs_reload(self) -> bool:
        """Objects are static."""
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
        """Load object as tool."""
        try:
            if callable(self.obj):
                # Extract metadata using helper function
                metadata = extract_tool_metadata(self.obj, self.config_overrides)

                if metadata:
                    tool = self._create_tool_container(
                        name=metadata["name"],
                        description=metadata["description"],
                        function=self.obj,
                        props=metadata["props"],
                        hidden_props=metadata["hidden_props"],
                        param_descriptions=metadata["param_descriptions"],
                        partial=metadata["partial"]
                    )

                    self.cached_tools = [tool]
                else:
                    # Create basic tool for non-decorated callables
                    tool = self._create_tool_container(
                        name=getattr(self.obj, '__name__', 'unknown_tool'),
                        description=getattr(self.obj, '__doc__',
                                            'No description available') or 'No description available',
                        function=self.obj
                    )

                    self.cached_tools = [tool]
            else:
                self.cached_tools = []

            self.last_load_time = time.time()
            self.error_state = None

        except Exception as e:
            self.error_state = f"Failed to load object as tool: {str(e)}"
            self.cached_tools = []
