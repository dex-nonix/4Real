from typing import Dict, Any, TYPE_CHECKING

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.plugin.base_plugin import api_services
from nonix_web.plugin.descriptor import InjectPlugin
from nonix_web.utils.di import di_register
from .llm.agentic_tool_manager import AgenticToolManager
from .routers.ai_analysis_result import AIAnalysisResultRouter
from .routers.ai_model_mapping import AIModelMappingRouter
from .routers.ai_provider import AIProviderRouter
from .routers.chat.chat_router import ChatRouter
from .routers.chat_history import ChatHistoryRouter
from .routers.chat_message import ChatMessageRouter
from .routers.chat_session import ChatSessionRouter
from .routers.chat_prompt import ChatPromptRouter
from .routers.internal_tool import InternalToolRouter
from .routers.mcp_server import MCPServerRouter
from .routers.persona import PersonaRouter
from .routers.persona_mcp_server import PersonaMCPServerRouter
from .routers.persona_tool_access import PersonaToolAccessRouter
from .routers.tool_invocation_log import ToolInvocationLogRouter

if TYPE_CHECKING:
    from nonix_web.server import NxWebServer
    from nonix_template.plugin import NxWebTemplatePlugin


@api_services([
    AIAnalysisResultRouter,
    AIModelMappingRouter,
    AIProviderRouter,
    ChatRouter,
    ChatHistoryRouter,
    ChatMessageRouter,
    ChatSessionRouter,
    ChatPromptRouter,
    InternalToolRouter,
    MCPServerRouter,
    PersonaRouter,
    PersonaMCPServerRouter,
    PersonaToolAccessRouter,
    ToolInvocationLogRouter
])
class NxWebAgenticPlugin(BasePlugin):
    agentic_tool_manager: AgenticToolManager = None
    template_plugin: "NxWebTemplatePlugin" = InjectPlugin("template")

    def _configure(self, server: "NxWebServer", config: Dict[str, Any]):
        self.agentic_tool_manager = AgenticToolManager()
        di_register(AgenticToolManager, instance=self.agentic_tool_manager)

    async def _startup(self, server: "NxWebServer", config: Dict[str, Any]):
        """Register template directory during startup"""
        # Register the agentic plugin's template directory
        from pathlib import Path

        template_dir = Path(__file__).parent / "templates"
        if template_dir.exists():
            try:
                self.template_plugin.add_search_path(str(template_dir))
                self._logger.info(f"Registered template directory: {template_dir}")
            except Exception as e:
                self._logger.warning(f"Failed to register template directory: {e}")
