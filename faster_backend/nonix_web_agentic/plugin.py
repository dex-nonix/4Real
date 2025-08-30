from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from nonix_web.utils.di import di_register
from .llm.agentic_tool_manager import AgenticToolManager
from .llm.llm_tool_mixin import LLMToolMixin
from .services.ai_analysis_result import AIAnalysisResultService
from .services.ai_model_mapping import AIModelMappingService
from .services.ai_provider import AIProviderService
from .services.chat.chat_service import ChatService
from .services.chat_history import ChatHistoryService
from .services.chat_message import ChatMessageService
from .services.chat_session import ChatSessionService
from .services.internal_tool import InternalToolService
from .services.mcp_server import MCPServerService
from .services.persona import PersonaService
from .services.persona_mcp_server import PersonaMCPServerService
from .services.persona_tool_access import PersonaToolAccessService
from .services.tool_invocation_log import ToolInvocationLogService


class NxWebAgenticPlugin(BasePlugin, LLMToolMixin):
    api_services = [
        AIAnalysisResultService,
        AIModelMappingService,
        AIProviderService,
        ChatService,
        ChatHistoryService,
        ChatMessageService,
        ChatSessionService,
        InternalToolService,
        MCPServerService,
        PersonaService,
        PersonaMCPServerService,
        PersonaToolAccessService,
        ToolInvocationLogService
    ]

    llm_tools = [
        # Built-in agentic tools can be added here
        # ("admin:system_info", _admin_system_info, "Get system information"),
    ]

    agentic_tool_manager: AgenticToolManager = None

    def _configure(self, server: "NxWebServer", config: Dict[str, Any]):
        self.agentic_tool_manager = AgenticToolManager()
        di_register(AgenticToolManager, instance=self.agentic_tool_manager)
