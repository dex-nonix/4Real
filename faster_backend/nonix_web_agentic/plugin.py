from typing import Dict, Any, TYPE_CHECKING

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.plugin.base_plugin import api_services
from nonix_web.plugin.descriptor import InjectPlugin
from nonix_web.utils.di import di_register
from .llm.agentic_tool_manager import AgenticToolManager
from .services.ai_analysis_result import AIAnalysisResultService
from .services.ai_model_mapping import AIModelMappingService
from .services.ai_provider import AIProviderService
from .services.chat.chat_service import ChatService
from .services.chat_history import ChatHistoryService
from .services.chat_message import ChatMessageService
from .services.chat_session import ChatSessionService
from .services.chat_prompt import ChatPromptService
from .services.internal_tool import InternalToolService
from .services.mcp_server import MCPServerService
from .services.persona import PersonaService
from .services.persona_mcp_server import PersonaMCPServerService
from .services.persona_tool_access import PersonaToolAccessService
from .services.tool_invocation_log import ToolInvocationLogService

if TYPE_CHECKING:
    from nonix_web.server import NxWebServer
    from nonix_template.plugin import NxWebTemplatePlugin


@api_services([
    AIAnalysisResultService,
    AIModelMappingService,
    AIProviderService,
    ChatService,
    ChatHistoryService,
    ChatMessageService,
    ChatSessionService,
    ChatPromptService,
    InternalToolService,
    MCPServerService,
    PersonaService,
    PersonaMCPServerService,
    PersonaToolAccessService,
    ToolInvocationLogService
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
        import os
        from pathlib import Path

        template_dir = Path(__file__).parent / "templates"
        if template_dir.exists():
            try:
                await self.template_plugin.add_search_path(str(template_dir))
                self._logger.info(f"Registered template directory: {template_dir}")
            except Exception as e:
                self._logger.warning(f"Failed to register template directory: {e}")
