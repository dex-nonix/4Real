from pathlib import Path
from typing import Any, Dict

from nonix_di.decorator import injectables
from nonix_plugin.base import BasePlugin
from nonix_plugin.descriptor import NxInjectPlugin
from nonix_web.decorator import web_routers
from .llm.agentic_tool_manager import AgenticToolManager
from .routers.ai_analysis_result_router import AIAnalysisResultRouter
from .routers.ai_model_mapping_router import AIModelMappingRouter
from .routers.ai_provider_router import AIProviderRouter
from .routers.chat_history_router import ChatHistoryRouter
from .routers.chat_message_router import ChatMessageRouter
from .routers.chat_prompt_router import ChatPromptRouter
from .routers.chat_router import ChatRouter
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


@web_routers([
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
@injectables([
    AgenticToolManager,
    AIAnalysisResultService,
    AIModelMappingService,
    AIProviderService,
    ChatHistoryService,
    ChatMessageService,
    ChatSessionService,
    ChatPromptService,
    InternalToolService,
    MCPServerService,
    PersonaService,
    PersonaMCPServerService,
    PersonaToolAccessService,
    ToolInvocationLogService,
    ToolExecutionService
])
class NxWebAgenticPlugin(BasePlugin):
    template_plugin = NxInjectPlugin("template")

    async def _startup(self, config: Dict[str, Any]):
        self.template_plugin.add_search_path(str(Path(__file__).parent / "templates"))
