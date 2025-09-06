from typing import Dict, Any, TYPE_CHECKING

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.plugin.base_plugin import routers
from nonix_web.plugin.descriptor import InjectPlugin
from nonix_web.utils.di import di_register
from .llm.agentic_tool_manager import AgenticToolManager
from .routers.ai_analysis_result_router import AIAnalysisResultRouter
from .routers.ai_model_mapping_router import AIModelMappingRouter
from .routers.ai_provider_router import AIProviderRouter
from .routers.chat.chat_router import ChatRouter
from .routers.chat_history_router import ChatHistoryRouter
from .routers.chat_message_router import ChatMessageRouter
from .routers.chat_prompt_router import ChatPromptRouter
from .routers.chat_session_router import ChatSessionRouter
from .routers.internal_tool_router import InternalToolRouter
from .routers.mcp_server_router import MCPServerRouter
from .routers.persona_mcp_server_router import PersonaMCPServerRouter
from .routers.persona_router import PersonaRouter
from .routers.persona_tool_access_router import PersonaToolAccessRouter
from .routers.tool_invocation_log_router import ToolInvocationLogRouter
from .services.ai_analysis_result_service import AIAnalysisResultService
from .services.ai_model_mapping_service import AIModelMappingService
from .services.ai_provider_service import AIProviderService
from .services.chat_history_service import ChatHistoryService
from .services.chat_message_service import ChatMessageService
from .services.chat_prompt_service import ChatPromptService
from .services.chat_session_service import ChatSessionService
from .services.internal_tool_service import InternalToolService
from .services.mcp_server_service import MCPServerService
from .services.persona_mcp_server_service import PersonaMCPServerService
from .services.persona_service import PersonaService
from .services.persona_tool_access_service import PersonaToolAccessService
from .services.tool_execution_service import ToolExecutionService
from .services.tool_invocation_log_service import ToolInvocationLogService

if TYPE_CHECKING:
    from nonix_web.server import NxWebServer
    from nonix_template.plugin import NxWebTemplatePlugin


@routers([
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

        # Register all CRUD services
        di_register(AIAnalysisResultService)
        di_register(AIModelMappingService)
        di_register(AIProviderService)
        di_register(ChatHistoryService)
        di_register(ChatMessageService)
        di_register(ChatSessionService)
        di_register(ChatPromptService)
        di_register(InternalToolService)
        di_register(MCPServerService)
        di_register(PersonaService)
        di_register(PersonaMCPServerService)
        di_register(PersonaToolAccessService)
        di_register(ToolInvocationLogService)
        di_register(ToolExecutionService)

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
