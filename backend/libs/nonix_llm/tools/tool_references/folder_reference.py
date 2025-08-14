import json
from importlib import import_module

import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from .base import ToolReference
from .. import extract_tool_metadata
from ..utils import resolve_safe_path


class FolderReference(ToolReference):
    """Reference to tools in JSON files within a folder with change detection."""

    def __init__(self, source: str, config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)
        self.folder_path = Path(source)
        self.file_timestamps = {}

    def needs_reload(self) -> bool:
        """Check if any JSON files in folder have changed."""
        if not self.folder_path.exists():
            return False

        current_timestamps = {}
        for json_file in self.folder_path.rglob("*.json"):
            current_timestamps[str(json_file)] = json_file.stat().st_mtime

        return current_timestamps != self.file_timestamps

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
        """Load tools from all JSON files in folder."""
        try:
            # Use secure path resolution
            safe_folder = resolve_safe_path(str(self.folder_path))
            safe_folder_path = Path(safe_folder)

            tools = []
            self.file_timestamps = {}

            for json_file in safe_folder_path.rglob("*.json"):
                self.file_timestamps[str(json_file)] = json_file.stat().st_mtime

                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

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

                except (json.JSONDecodeError, PermissionError) as e:
                    print(f"Error loading {json_file}: {str(e)}")
                    continue

            self.cached_tools = tools
            self.last_load_time = time.time()
            self.error_state = None

        except (PermissionError, OSError) as e:
            self.error_state = f"Failed to access folder {self.source}: {str(e)}"
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
