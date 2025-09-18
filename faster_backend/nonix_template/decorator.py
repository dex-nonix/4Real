import os
from pathlib import Path
from typing import List, Optional
import logging

from nonix_plugin import add_configure_callback
from nonix_di.resolve import di_resolve
from .services.template_service import TemplateService


logger = logging.getLogger(__name__)


def templates(directories: Optional[List[str]] = None,
              discover: bool = True):
    """
    Decorator for automatic template loading and registration.

    This decorator automatically loads templates from specified directories
    and can auto-discover templates from the plugin's template directory.

    Args:
        directories: List of directories to load templates from.
                    If None, only auto-discovery is used.
        discover: Whether to auto-discover templates from plugin's ./templates/ directory.
                 Defaults to True for convenience.

    Example:
        # Simple auto-loading
        @templates()
        class MyPlugin(BasePlugin): pass

        # Custom directories + auto-discovery
        @templates(["./custom_templates"], discover=True)
        class MyPlugin(BasePlugin): pass

        # Only custom directories, no auto-discovery
        @templates(["/path/to/templates"], discover=False)
        class MyPlugin(BasePlugin): pass
    """
    def decorator(cls):
        # Skip if no directories specified and discover is disabled
        if not directories and not discover:
            return cls

        @add_configure_callback
        def _load_templates(plugin, config):
            try:
                # Get template service
                template_service = di_resolve(TemplateService)
                if not template_service:
                    logger.warning("TemplateService not available for template loading")
                    return

                # Collect all directories to load from
                all_directories = []
                plugin_templates_loaded = False

                # Add custom directories first (higher priority)
                if directories:
                    for directory in directories:
                        try:
                            # Convert to absolute path relative to plugin if relative
                            if not Path(directory).is_absolute():
                                # Use the reliable plugin directory from plugin system
                                if plugin.plugin_dir:
                                    abs_directory = plugin.plugin_dir / directory
                                else:
                                    abs_directory = Path(directory).resolve()
                            else:
                                abs_directory = Path(directory).resolve()

                            all_directories.append(str(abs_directory))
                            logger.debug(f"Added custom template directory: {abs_directory}")

                        except Exception as e:
                            logger.warning(f"Failed to resolve template directory '{directory}': {e}")

                # Auto-discover plugin's template directory
                if discover:
                    if plugin.plugin_dir:
                        plugin_template_dir = plugin.plugin_dir / 'templates'
                        if plugin_template_dir.exists():
                            # Insert at beginning for lower priority (can be overridden by custom dirs)
                            all_directories.insert(0, str(plugin_template_dir))
                            plugin_templates_loaded = True
                            logger.debug(f"Auto-discovered plugin template directory: {plugin_template_dir}")
                        else:
                            logger.debug(f"No plugin template directory found for {plugin.name}")

                # Load templates from all directories
                loaded_count = 0
                for directory in all_directories:
                    try:
                        template_service.add_search_path(directory)
                        loaded_count += 1
                        logger.info(f"Loaded templates from: {directory}")
                    except Exception as e:
                        logger.warning(f"Failed to load templates from '{directory}': {e}")

                # Log summary
                if loaded_count > 0:
                    if plugin_templates_loaded:
                        logger.info(f"Template decorator loaded {loaded_count} directories for {plugin.name} (including plugin templates)")
                    else:
                        logger.info(f"Template decorator loaded {loaded_count} directories for {plugin.name}")
                else:
                    logger.warning(f"Template decorator found no valid directories for {plugin.name}")

            except Exception as e:
                logger.error(f"Template decorator failed for {plugin.name}: {e}")

        return _load_templates(cls)

    return decorator


