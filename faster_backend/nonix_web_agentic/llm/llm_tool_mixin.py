import logging
from typing import Dict, Any, List, Tuple, Callable, Optional

from nonix_web.utils.di import Inject


class LLMToolMixin:
    """Mixin for automatic LLM tool registration in plugins.
    
    Usage:
        class MyPlugin(BasePlugin, LLMToolMixin):
            llm_tools = [
                ("namespace:tool_name", function, "Tool description"),
                ("music:artist_info", artist_get_info, "Get artist information"),
            ]
    """
    
    llm_tools: List[Tuple[str, Callable, str]] = []
    agentic_tool_manager = Inject("AgenticToolManager")

    async def _startup(self, server: "NxWebServer", config: Dict[str, Any]):
        """Automatically register LLM tools during plugin startup."""
        await self._register_llm_tools()

    async def _register_llm_tools(self):
        """Register all LLM tools defined in the llm_tools array."""
        if not hasattr(self, 'agentic_tool_manager') or not self.agentic_tool_manager:
            self._logger.warning("AgenticToolManager not available, skipping LLM tool registration")
            return

        if not self.llm_tools:
            self._logger.debug("No LLM tools defined for this plugin")
            return

        registered_count = 0
        failed_count = 0

        for qualified_name, func, description in self.llm_tools:
            try:
                # Validate tool definition
                if not isinstance(qualified_name, str) or not qualified_name:
                    self._logger.error(f"Invalid qualified_name for tool: {qualified_name}")
                    failed_count += 1
                    continue
                
                if not callable(func):
                    self._logger.error(f"Tool {qualified_name} is not callable")
                    failed_count += 1
                    continue
                
                if not isinstance(description, str):
                    self._logger.warning(f"Tool {qualified_name} has no description, using default")
                    description = f"Execute {qualified_name}"

                # Register the tool
                self.agentic_tool_manager.register(qualified_name, func)
                self._logger.info(f"Registered LLM tool: {qualified_name} - {description}")
                registered_count += 1

            except Exception as e:
                self._logger.error(f"Failed to register tool {qualified_name}: {e}")
                failed_count += 1

        if registered_count > 0:
            self._logger.info(f"Successfully registered {registered_count} LLM tools")
        
        if failed_count > 0:
            self._logger.warning(f"Failed to register {failed_count} LLM tools")

    def _validate_tool_definition(self, tool_def: Tuple) -> bool:
        """Validate a single tool definition tuple."""
        if not isinstance(tool_def, tuple) or len(tool_def) != 3:
            return False
        
        qualified_name, func, description = tool_def
        
        if not isinstance(qualified_name, str) or not qualified_name:
            return False
        
        if not callable(func):
            return False
        
        if not isinstance(description, str):
            return False
        
        return True
