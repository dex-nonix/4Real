from typing import Optional, Dict, Any, List

from .base import ToolReference


class NestedManagerReference(ToolReference):
    """Reference to another NxLLMToolsManager instance with circular detection."""

    def __init__(self, source: 'NxLLMToolsManager', config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)
        self.manager = source
        self._visiting = False  # Circular reference detection

    def needs_reload(self) -> bool:
        """Always check nested manager for changes."""
        return True

    def reload(self) -> None:
        """Reload is handled by get_tools method."""
        pass

    def get_tools(self, context: Optional[Dict[str, Any]] = None,
                  partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tools from nested manager with circular reference detection."""
        if self.disabled:
            return []

        if self._visiting:
            # Circular reference detected
            return []

        try:
            self._visiting = True
            return self.manager.get_all_tools(context, partial_map)
        except Exception as e:
            print(f"Error getting tools from nested manager: {str(e)}")
            return []
        finally:
            self._visiting = False
