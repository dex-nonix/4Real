# plugin_system.py

import sys
import json
import importlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from fastapi import FastAPI
import logging

# Configure a simple logger for the plugin system
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("plugin_loader")


class BasePlugin(ABC):
    """
    The base class for all plugins.

    Plugins should inherit from this class. The `load_plugin` method
    is called by the plugin loader, allowing the plugin to register
    its routes or perform other setup tasks.
    """

    def __init__(self):
        # You can retrieve metadata here if needed later
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"


    @abstractmethod
    async def load_plugin(self, app: FastAPI):
        """
        This method is called by the loader. Overload this in your plugin
        to integrate with the FastAPI application, e.g., by adding routers.

        Args:
            app: The main FastAPI application instance.
        """
        log.info(f"Default load_plugin called for {self.name}. "
                 "Consider overriding this method in your plugin.")


async def load_plugins(app: FastAPI, plugins_path: str):
    """
    Loads all valid plugins from a single directory path.

    Args:
        app: The FastAPI application instance.
        plugins_path: The string path to a directory containing plugin packages.
    """
    plugins_dir = Path(plugins_path).resolve()

    if not plugins_dir.is_dir():
        log.error(f"Plugin path '{plugins_dir}' is not a valid directory. Skipping.")
        return

    # Add the parent plugins directory to the Python path if not already there
    if str(plugins_dir) not in sys.path:
        sys.path.insert(0, str(plugins_dir))
        log.info(f"Added '{plugins_dir}' to system path.")

    # Iterate over each potential plugin package in the directory
    for item in plugins_dir.iterdir():
        if not item.is_dir():
            continue

        plugin_json_path = item / "plugin.json"
        if not plugin_json_path.exists():
            continue  # Not a valid plugin if it lacks plugin.json

        log.info(f"Found potential plugin in: '{item.name}'")

        try:
            # 1. Read metadata from plugin.json
            with open(plugin_json_path, "r") as f:
                metadata = json.load(f)

            plugin_name = metadata.get("name", item.name)
            plugin_version = metadata.get("version", "N/A")
            module_name = metadata.get("module", "plugin")
            class_name = metadata.get("class", "Plugin")

            # The import path is `package_name.module_name`
            # e.g., "plugin_one.plugin"
            import_path = f"{item.name}.{module_name}"

            # 2. Dynamically import the module
            log.info(f"Attempting to load module: '{import_path}'")
            module = importlib.import_module(import_path)

            # 3. Get the plugin class from the module
            log.info(f"Attempting to get class '{class_name}' from module.")
            PluginClass = getattr(module, class_name)

            # 4. Instantiate the plugin
            plugin_instance = PluginClass()

            # 5. Validate that it's a proper plugin
            if not isinstance(plugin_instance, BasePlugin):
                log.error(f"Plugin '{plugin_name}' class '{class_name}' does not inherit from BasePlugin. Skipping.")
                continue

            # Assign metadata to the instance
            plugin_instance.name = plugin_name
            plugin_instance.version = plugin_version

            # 6. Load the plugin into the app
            log.info(f"Loading plugin: '{plugin_instance.name}' version {plugin_instance.version}")
            await plugin_instance.load_plugin(app)

        except (ImportError, AttributeError, json.JSONDecodeError, Exception) as e:
            log.error(f"Failed to load plugin from '{item.name}': {e}", exc_info=True)


async def load_all_plugins(app: FastAPI, plugin_paths: List[str]):
    """
    Loads plugins from a list of directory paths.

    Args:
        app: The FastAPI application instance.
        plugin_paths: A list of string paths to directories.
    """
    log.info(f"Starting plugin loading from paths: {plugin_paths}")
    for path in plugin_paths:
        await load_plugins(app, path)