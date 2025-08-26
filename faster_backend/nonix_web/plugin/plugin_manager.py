import importlib
import json
import logging
import sys
from pathlib import Path
from typing import Union, List, Dict, Any, TYPE_CHECKING

from .base_plugin import BasePlugin

if TYPE_CHECKING:
    from ..server import NxWebServer


class PluginManager:
    def __init__(self, server: "NxWebServer", plugin_paths: Union[str, List[str]]):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.server = server
        self.plugin_paths = [Path(p).resolve() for p in
                             ([plugin_paths] if isinstance(plugin_paths, str) else plugin_paths)]
        self.available_plugins: Dict[str, Dict[str, Any]] = {}
        self.loaded_plugins: Dict[str, "BasePlugin"] = {}

        self._add_paths_to_sys()

    def _add_paths_to_sys(self):
        for path in self.plugin_paths:
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
                self._logger.info(f"Added '{path}' to system path.")

    def discover_plugins(self):
        """
        Scans the plugin directories and registers available plugins based on their metadata.
        This step does not load the plugins.
        """
        self._logger.info("Starting plugin discovery...")
        for plugins_dir in self.plugin_paths:
            if not plugins_dir.is_dir():
                self._logger.error(f"Plugin path '{plugins_dir}' is not a valid directory. Skipping.")
                continue

            for item in plugins_dir.iterdir():
                if not item.is_dir():
                    continue

                plugin_json_path = item / "plugin.json"
                if not plugin_json_path.exists():
                    continue

                try:
                    with open(plugin_json_path, "r") as f:
                        metadata = json.load(f)

                    plugin_name = metadata.get("name", item.name)
                    if not plugin_name:
                        self._logger.warning(f"Plugin in '{item.name}' has no name. Skipping.")
                        continue

                    self.available_plugins[plugin_name] = {
                        "path": item,
                        "metadata": metadata
                    }
                    self._logger.debug(f"Discovered plugin '{plugin_name}' at {item}")
                except (json.JSONDecodeError, Exception) as e:
                    self._logger.error(f"Failed to read metadata for plugin in '{item.name}': {e}", exc_info=True)
        self._logger.info(f"Discovery complete. Found {len(self.available_plugins)} available plugins.")

    async def load_plugins(self, plugins_to_load: List[Union[str, Dict[str, Any]]]):
        """
        Loads a specified list of plugins and their dependencies in the correct order.
        """
        self._logger.info("Starting to load specified plugins and their dependencies.")
        load_order = self._resolve_dependencies(plugins_to_load)

        for plugin_info in load_order:
            plugin_name = plugin_info if isinstance(plugin_info, str) else plugin_info.get("name")

            if not plugin_name or plugin_name in self.loaded_plugins:
                continue

            override_config = plugin_info.get("config", {}) if isinstance(plugin_info, dict) else {}

            plugin_data = self.available_plugins.get(plugin_name)
            if not plugin_data:
                self._logger.error(f"Cannot load plugin '{plugin_name}': Not found in available plugins.")
                continue

            await self._load_plugin(plugin_name, plugin_data, override_config)

    def _resolve_dependencies(self, plugins_to_load: List[Union[str, Dict[str, Any]]]) -> List[
        Union[str, Dict[str, Any]]]:
        resolved = []
        visiting = set()
        plugin_map = {
            (p if isinstance(p, str) else p.get("name")): p for p in plugins_to_load
        }

        def visit(plugin_name):
            if plugin_name in resolved:
                return
            if plugin_name in visiting:
                raise Exception(f"Circular dependency detected in plugins involving '{plugin_name}'")

            visiting.add(plugin_name)

            plugin_data = self.available_plugins.get(plugin_name)
            if not plugin_data:
                raise Exception(f"Dependency '{plugin_name}' not found.")

            dependencies = plugin_data.get("metadata", {}).get("dependencies", [])
            for dep in dependencies:
                visit(dep)

            visiting.remove(plugin_name)
            resolved.append(plugin_name)

        for plugin_info in plugins_to_load:
            plugin_name = plugin_info if isinstance(plugin_info, str) else plugin_info.get("name")
            if plugin_name:
                visit(plugin_name)

        # Return the plugins with their original config overrides
        return [plugin_map.get(name, name) for name in resolved]

    async def _load_plugin(self, plugin_name: str, plugin_data: Dict[str, Any], override_config: Dict[str, Any]):
        plugin_dir = plugin_data["path"]
        metadata = plugin_data["metadata"]

        try:
            default_config = metadata.get("config", {})
            final_config = {**default_config, **override_config}

            module_name = metadata.get("module", "plugin")
            class_name = metadata.get("class", "Plugin")
            import_path = f"{plugin_dir.name}.{module_name}"

            self._logger.debug(f"Attempting to load module: '{import_path}'")
            module = importlib.import_module(import_path)

            self._logger.debug(f"Attempting to get class '{class_name}' from module.")

            PluginClass = getattr(module, class_name)
            plugin_instance = PluginClass(config=final_config)

            if not isinstance(plugin_instance, BasePlugin):
                self._logger.error(
                    f"Plugin '{plugin_name}' class '{class_name}' does not inherit from BasePlugin. Skipping.")
                return

            plugin_instance.name = plugin_name
            plugin_instance.version = metadata.get("version", "0.0.0")

            self._logger.info(f"Loading plugin: '{plugin_instance.name}' version {plugin_instance.version}")
            await plugin_instance.load_plugin(self.server, plugin_instance.config)
            self.loaded_plugins[plugin_name] = plugin_instance

        except (ImportError, AttributeError, Exception) as e:
            self._logger.error(f"Failed to load plugin from '{plugin_dir.name}': {e}", exc_info=True)

    async def discover_and_load(self, plugins_to_load):
        self.discover_plugins()
        await self.load_plugins(plugins_to_load)
