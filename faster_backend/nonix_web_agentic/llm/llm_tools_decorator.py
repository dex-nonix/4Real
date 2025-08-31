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
            name = tool[0]
            func = tool[1]
            if isinstance(func, str):
                func = getattr(plugin, func)
            tool_manager.register_tool(name,func)

    return lambda cls: add_configure_callback(cls, _add_tools)