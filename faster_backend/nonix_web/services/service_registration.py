from .ai_analysis_result import AIAnalysisResultService
from .ai_model_mapping import AIModelMappingService
from .ai_provider import AIProviderService
from .album import AlbumService
from .artist.artist_service import ArtistService
from .chat import ChatService
from .chat_history import ChatHistoryService
from .chat_message import ChatMessageService
from .chat_session import ChatSessionService
from .file import FileService
from .file_category import FileCategoryService
from .file_link import FileLinkService
from .internal_tool import InternalToolService
from .mcp_server import MCPServerService
from .persona.persona_service import PersonaService
from .persona_mcp_server import PersonaMCPServerService
from .persona_tool_access import PersonaToolAccessService
from .rhyme_technique import RhymeTechniqueService
from .style.style_service import StyleService
from .tool_invocation_log import ToolInvocationLogService
from .track import TrackService

ALL_SERVICES = [
    lambda app: ChatService.to_router(app=app),
    ArtistService,
    AlbumService,
    AIAnalysisResultService,
    AIModelMappingService,
    AIProviderService,
    ChatHistoryService,
    ChatMessageService,
    ChatSessionService,
    FileCategoryService,
    FileLinkService,
    FileService,
    InternalToolService,
    MCPServerService,
    PersonaMCPServerService,
    PersonaService,
    PersonaToolAccessService,
    RhymeTechniqueService,
    StyleService,
    ToolInvocationLogService,
    TrackService,

]
