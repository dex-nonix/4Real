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
import NotFound from "@/views/NotFound.vue";
import Home from "@/views/Home.vue";
import About from "@/views/About.vue";
import DynamicFormExample from "@/views/DynamicFormExample.vue";
import DynamicTableExample from "@/views/DynamicTableExample.vue";
import Chat from "@/views/Chat.vue";

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
    },
    routes: [

        // Regular routes
        {path: '/', name: 'home', component: Home, meta: {layout: 'master'}},
        {path: '/about', name: 'about', component: About, meta: {layout: 'alt'}},
        {path: '/dynamic-form', name: 'dynamic-form', component: DynamicFormExample, meta: {layout: 'master'}},
        {path: '/dynamic-table', name: 'dynamic-table', component: DynamicTableExample, meta: {layout: 'master'}},
        {path: '/chat', name: 'chat', component: Chat, meta: {layout: 'master'}},

        // Dynamic route
        {

            type: "dynamic",
            path: '/dashboard',
            page: 'dashboard',
            meta: {layout: 'master'}
        },

        // CRUD routes
        {type: "crud", entity: 'albums'},
        {type: "crud", entity: 'tracks'},
        {type: "crud", entity: 'styles'},
        {type: "crud", entity: 'rhyme-techniques'},
        {type: "crud", entity: 'ai-providers'},
        {type: "crud", entity: 'ai-model-mappings'},
        {type: "crud", entity: 'ai-analysis-results'},
        {type: "crud", entity: 'artists'},
        {type: "crud", entity: 'personas'},
        {type: "crud", entity: 'internal-tools'},
        {type: "crud", entity: 'persona-tool-access'},
        {type: "crud", entity: 'mcp-servers'},
        {type: "crud", entity: 'persona-mcp-servers'},
        {type: "crud", entity: 'chat-sessions'},
        {type: "crud", entity: 'chat-messages'},
        {type: "crud", entity: 'tool-invocation-logs'},
        {type: "crud", entity: 'file-categories'},
        {type: "crud", entity: 'files'},
        {type: "crud", entity: 'file-links'},

        // 404 route
        {path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: {layout: 'alt'}},
    ]
};



