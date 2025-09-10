import ArtistService from '@/services/ArtistService.js'
import AlbumService from '@/services/AlbumService.js'
import TrackService from '@/services/TrackService.js'
import StyleService from '@/services/StyleService.js'
import TemplateService from '@/services/TemplateService.js'
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
import ChatHistoryService from '@/services/ChatHistoryService.js'
import ChatMessageService from '@/services/ChatMessageService.js'
import ChatPromptService from '@/services/ChatPromptService.js'
import ToolInvocationLogService from '@/services/ToolInvocationLogService.js'

import FileService from '@nonix-file-manager/services/FileService.js'
import FileLinkService from '@nonix-file-manager/services/FileLinkService.js'
import FileCategoryService from "@nonix-file-manager/services/FileCategoryService.js";
import ChatService from '@nonix-chat/services/ChatService.js'
import Home from "@/views/Home.vue";
import About from "@/views/About.vue";
import DynamicFormExample from "@/views/DynamicFormExample.vue";
import DynamicTableExample from "@/views/DynamicTableExample.vue";


export const appConfig = {

    routes: [

        // Regular routes
        {path: '/', name: 'home', component: Home},
        {path: '/about', name: 'about', component: About, meta: {layout: 'alt'}},
        {path: '/dynamic-form', name: 'dynamic-form', component: DynamicFormExample},

        {path: '/dynamic-table', name: 'dynamic-table', component: DynamicTableExample, meta: {layout: "advanced"}},

        // Dynamic route
        {type: "dynamic", path: '/dashboard', page: 'dashboard'},

        // CRUD routes
        {type: "crud", entity: 'albums'},
        {type: "crud", entity: 'tracks'},
        {type: "crud", entity: 'styles'},
        {type: "crud", entity: 'templates'},
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
        {type: "crud", entity: 'chat-histories'},
        {type: "crud", entity: 'chat-messages'},
        {type: "crud", entity: 'chat-prompts'},
        {type: "crud", entity: 'tool-invocation-logs'},
        {type: "crud", entity: 'file-categories'},
        {type: "crud", entity: 'files'},
        {type: "crud", entity: 'file-links'},

        // 404 route
        //{path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: {layout: 'alt'}},
    ],
    service: {
        "artists": (app) => new ArtistService(app),
        "albums": (app) => new AlbumService(app),
        "tracks": (app) => new TrackService(app),
        "styles": (app) => new StyleService(app),
        "templates": (app) => new TemplateService(app),
        "rhyme-techniques": (app) => new RhymeTechniqueService(app),
        "ai-providers": (app) => new AIProviderService(app),
        "ai-model-mappings": (app) => new AIModelMappingService(app),
        "ai-analysis-results": (app) => new AIAnalysisResultService(app),
        "personas": (app) => new PersonaService(app),
        "internal-tools": (app) => new InternalToolService(app),
        "persona-tool-access": (app) => new PersonaToolAccessService(app),
        "mcp-servers": (app) => new MCPServerService(app),
        "persona-mcp-servers": (app) => new PersonaMCPServerService(app),
        "chat-sessions": (app) => new ChatSessionService(app),
        "chat-histories": (app) => new ChatHistoryService(app),
        "chat-messages": (app) => new ChatMessageService(app),
        "chat-prompts": (app) => new ChatPromptService(app),
        "tool-invocation-logs": (app) => new ToolInvocationLogService(app),
        "file-categories": (app) => new FileCategoryService(app),
        "files": (app) => new FileService(app),
        "file-links": (app) => new FileLinkService(app),
        "chat-service": (app) => new ChatService(app),
    },
    use: [],
    layouts: {},
    pages: {},
    displayWidgets: {},
    editWidgets: {},
    dynamicWidgets: {},
    packages: [
        /*
        {
            service: [],
            use: [],
            layouts: {},
            pages: {},
            displayWidgets: {},
            editWidgets: {},
            dynamicWidgets: {},
        }
        */
    ]
};



