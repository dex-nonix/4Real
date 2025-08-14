import ArtistService from '@/services/ArtistService.js'
import AlbumService from '@/services/AlbumService.js'
import TrackService from '@/services/TrackService.js'
import StyleService from '@/services/StyleService.js'
import RhymeTechniqueService from '@/services/RhymeTechniqueService.js'
import AIProviderService from '@/services/AIProviderService.js'
import AIModelMappingService from '@/services/AIModelMappingService.js'
import AIAnalysisResultService from '@/services/AIAnalysisResultService.js'
import PersonaService from '@/services/PersonaService.js'
import InternalToolService from '@/services/InternalToolService.js'
import PersonaToolAccessService from '@/services/PersonaToolAccessService.js'
import MCPServerService from '@/services/MCPServerService.js'
import PersonaMCPServerService from '@/services/PersonaMCPServerService.js'
import ChatSessionService from '@/services/ChatSessionService.js'
import ChatMessageService from '@/services/ChatMessageService.js'
import ToolInvocationLogService from '@/services/ToolInvocationLogService.js'
import FileCategoryService from '@/services/FileCategoryService.js'
import FileService from '@/services/FileService.js'
import FileLinkService from '@/services/FileLinkService.js'

export const appConfig = {
    service: {
        "artists": () => new ArtistService(),
        "albums": () => new AlbumService(),
        "tracks": () => new TrackService(),
        "styles": () => new StyleService(),
        "rhyme-techniques": () => new RhymeTechniqueService(),
        "ai-providers": () => new AIProviderService(),
        "ai-model-mappings": () => new AIModelMappingService(),
        "ai-analysis-results": () => new AIAnalysisResultService(),
        "personas": () => new PersonaService(),
        "internal-tools": () => new InternalToolService(),
        "persona-tool-access": () => new PersonaToolAccessService(),
        "mcp-servers": () => new MCPServerService(),
        "persona-mcp-servers": () => new PersonaMCPServerService(),
        "chat-sessions": () => new ChatSessionService(),
        "chat-messages": () => new ChatMessageService(),
        "tool-invocation-logs": () => new ToolInvocationLogService(),
        "file-categories": () => new FileCategoryService(),
        "files": () => new FileService(),
        "file-links": () => new FileLinkService(),
    }
};



