import NxArtistService from '@nonix-music-artist/services/NxArtistService.js'
import NxAlbumService from '@nonix-music-artist/services/NxAlbumService.js'
import NxTrackService from '@nonix-music-artist/services/NxTrackService.js'
import NxStyleService from '@nonix-music-artist/services/NxStyleService.js'
import NxTemplateService from '@nonix-template/services/NxTemplateService.js'
import NxRhymeTechniqueService from '@nonix-music-artist/services/NxRhymeTechniqueService.js'
import NxAIProviderService from '@nonix-chat/services/NxAIProviderService.js'
import NxAIModelMappingService from '@nonix-chat/services/NxAIModelMappingService.js'
import NxAIAnalysisResultService from '@nonix-chat/services/NxAIAnalysisResultService.js'
import NxPersonaService from '@nonix-chat/services/NxPersonaService.js'
import NxInternalToolService from '@nonix-chat/services/NxInternalToolService.js'
import NxPersonaToolAccessService from '@nonix-chat/services/NxPersonaToolAccessService.js'
import NxMCPServerService from '@nonix-chat/services/NxMCPServerService.js'
import NxPersonaMCPServerService from '@nonix-chat/services/NxPersonaMCPServerService.js'
import NxChatSessionService from '@nonix-chat/services/NxChatSessionService.js'
import NxChatHistoryService from '@nonix-chat/services/NxChatHistoryService.js'
import NxChatMessageService from '@nonix-chat/services/NxChatMessageService.js'
import NxChatPromptService from '@nonix-chat/services/NxChatPromptService.js'
import NxToolInvocationLogService from '@nonix-chat/services/NxToolInvocationLogService.js'

import NxFileService from '@nonix-file-manager/services/NxFileService.js'
import NxFileLinkService from '@nonix-file-manager/services/NxFileLinkService.js'
import NxFileCategoryService from "@nonix-file-manager/services/NxFileCategoryService.js";
import NxChatService from '@nonix-chat/services/NxChatService.js'
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
        "artists": (app) => new NxArtistService(app),
        "albums": (app) => new NxAlbumService(app),
        "tracks": (app) => new NxTrackService(app),
        "styles": (app) => new NxStyleService(app),
        "templates": (app) => new NxTemplateService(app),
        "rhyme-techniques": (app) => new NxRhymeTechniqueService(app),
        "ai-providers": (app) => new NxAIProviderService(app),
        "ai-model-mappings": (app) => new NxAIModelMappingService(app),
        "ai-analysis-results": (app) => new NxAIAnalysisResultService(app),
        "personas": (app) => new NxPersonaService(app),
        "internal-tools": (app) => new NxInternalToolService(app),
        "persona-tool-access": (app) => new NxPersonaToolAccessService(app),
        "mcp-servers": (app) => new NxMCPServerService(app),
        "persona-mcp-servers": (app) => new NxPersonaMCPServerService(app),
        "chat-sessions": (app) => new NxChatSessionService(app),
        "chat-histories": (app) => new NxChatHistoryService(app),
        "chat-messages": (app) => new NxChatMessageService(app),
        "chat-prompts": (app) => new NxChatPromptService(app),
        "tool-invocation-logs": (app) => new NxToolInvocationLogService(app),
        "file-categories": (app) => new NxFileCategoryService(app),
        "files": (app) => new NxFileService(app),
        "file-links": (app) => new NxFileLinkService(app),
        "chat-service": (app) => new NxChatService(app),
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



