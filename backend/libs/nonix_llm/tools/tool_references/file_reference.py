import json
from importlib import import_module

import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from .base import ToolReference
from .. import extract_tool_metadata
from ..utils import resolve_safe_path


class FileReference(ToolReference):
    """Reference to tools defined in a JSON file with change detection."""

    def __init__(self, source: str, config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)
        self.file_path = Path(source)
        self.last_modified = None

    def needs_reload(self) -> bool:
        """Check if file has been modified."""
        if not self.file_path.exists():
            return False

        current_modified = self.file_path.stat().st_mtime
        return self.last_modified != current_modified

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
        """Load tools from JSON file."""
        try:
            # Use secure path resolution
            safe_path = resolve_safe_path(str(self.file_path))

            with open(safe_path, 'r') as f:
                data = json.load(f)

            tools = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "func" in item:
                        tool = self._create_tool_from_config(item)
                        if tool:
                            tools.append(tool)
            elif isinstance(data, dict) and "func" in data:
                tool = self._create_tool_from_config(data)
                if tool:
                    tools.append(tool)

            self.cached_tools = tools
            self.last_modified = self.file_path.stat().st_mtime
            self.last_load_time = time.time()
            self.error_state = None

        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            self.error_state = f"Failed to load file {self.source}: {str(e)}"
            self.cached_tools = []

    def _create_tool_from_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create tool from configuration dictionary."""
        try:
            func_spec = config["func"]
            if ":" not in func_spec:
                return None

            module_path, symbol_name = func_spec.split(":", 1)
            module = import_module(module_path)
            function = getattr(module, symbol_name)

            # Apply config overrides
            merged_config = {**config, **self.config_overrides}
            metadata = extract_tool_metadata(function, merged_config)

            if metadata:
                return self._create_tool_container(
                    name=metadata["name"],
                    description=metadata["description"],
                    function=function,
                    props=metadata["props"],
                    hidden_props=metadata["hidden_props"],
                    param_descriptions=metadata["param_descriptions"],
                    partial=metadata["partial"]
                )

        except (ImportError, AttributeError, KeyError) as e:
            print(f"Error creating tool from config {config}: {str(e)}")

        return None
