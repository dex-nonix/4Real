from typing import TYPE_CHECKING

from nonix_web.plugin.base_plugin import add_configure_callback

from nonix_web.utils.di import di_resolve
from nonix_web_agentic.llm import AgenticToolManager

if TYPE_CHECKING:
    from nonix_web.server import NxWebServer

def llm_tools(tools):
    tool_manager:AgenticToolManager = None

    def _add_tools(plugin, server:"NxWebServer", config):
        nonlocal tool_manager
        if tool_manager is None:
            tool_manager = di_resolve(AgenticToolManager)
        for tool in tools:
            if isinstance(tool, tuple) and len(tool) == 2:
                # Traditional (name, func) tuple
                name = tool[0]
                func = tool[1]
                if isinstance(func, str):
                    func = getattr(plugin, func)
                tool_manager.register(name, func)
            elif hasattr(tool, 'to_agentic_tools'):
                # BaseToolService instance - extract tools using to_agentic_tools()
                service_tools = tool.to_agentic_tools()
                for name, func in service_tools:
                    tool_manager.register(name, func)

    return lambda cls: add_configure_callback(cls, _add_tools)