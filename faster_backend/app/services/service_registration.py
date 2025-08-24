from .ai_analysis_result import AIAnalysisResultService
from .ai_model_mapping import AIModelMappingService
from .ai_provider import AIProviderService
from .album import AlbumService
from .artist.artist_service import ArtistService
from .chat_history import ChatHistoryService
from .chat_message import ChatMessageService
from .chat_session import ChatSessionService
from .file import FileService
from .file_category import FileCategoryService
from .file_link import FileLinkService
from .internal_tool import InternalToolService
from .mcp_server import MCPServerService
from .persona_mcp_server import PersonaMCPServerService

ALL_SERVICES = [
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
    PersonaMCPServerService
]
