import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.health import router as health_router
from .api.upload import router as upload_router
from .config import settings
from .database import init_db, close_db
from .services.album import AlbumService
from .services.artist.artist_service import ArtistService
from .websocket.handlers import handle_websocket


async def register_all_services(service_router: "ServiceRouter", app: FastAPI) -> None:
    """Register all available services with the ServiceRouter."""

    # Import all service classes
    from .api.services.artist_service import ArtistService
    from .api.services.album_service import AlbumService
    from .api.services.track_service import TrackService
    from .api.services.file_service import FileService
    from .api.services.chat_service.chat_service import ChatService
    from .api.services.persona_service import PersonaService
    from .api.services.ai_analysis_result_service import AIAnalysisResultService
    from .api.services.ai_model_mapping_service import AIModelMappingService
    from .api.services.ai_provider_service import AIProviderService
    from .api.services.chat_history_service import ChatHistoryService
    from .api.services.chat_message_service import ChatMessageService
    from .api.services.chat_session_service import ChatSessionService
    from .api.services.file_category_service import FileCategoryService
    from .api.services.file_link_service import FileLinkService
    from .api.services.internal_tool_service import InternalToolService
    from .api.services.mcp_server_service import MCPServerService
    from .api.services.persona_mcp_server_service import PersonaMCPServerService
    from .api.services.persona_tool_access_service import PersonaToolAccessService
    from .api.services.rhyme_technique_service import RhymeTechniqueService
    from .api.services.style_service import StyleService
    from .api.services.tool_invocation_log_service import ToolInvocationLogService

    # Register CRUD services
    service_router.register_service("artists", ArtistService)
    service_router.register_service("albums", AlbumService)
    service_router.register_service("tracks", TrackService)
    service_router.register_service("personas", PersonaService)
    service_router.register_service("ai-analysis-results", AIAnalysisResultService)
    service_router.register_service("ai-model-mappings", AIModelMappingService)
    service_router.register_service("ai-providers", AIProviderService)
    service_router.register_service("chat-histories", ChatHistoryService)
    service_router.register_service("chat-messages", ChatMessageService)
    service_router.register_service("chat-sessions", ChatSessionService)
    service_router.register_service("file-categories", FileCategoryService)
    service_router.register_service("file-links", FileLinkService)
    service_router.register_service("internal-tools", InternalToolService)
    service_router.register_service("mcp-servers", MCPServerService)
    service_router.register_service("persona-mcp-servers", PersonaMCPServerService)
    service_router.register_service("persona-tool-access", PersonaToolAccessService)
    service_router.register_service("rhyme-techniques", RhymeTechniqueService)
    service_router.register_service("styles", StyleService)
    service_router.register_service("tool-invocation-logs", ToolInvocationLogService)

    # Register special services (with app parameter for ChatService)
    service_router.register_service("files", FileService)
    service_router.register_service("chat", ChatService, app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup/shutdown events."""
    # Startup
    service_router_instance = getattr(app.state, 'service_router_instance', None)
    if service_router_instance:
        await register_all_services(service_router_instance, app)

    await init_db()
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    yield

    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(ArtistService.to_router(), prefix="/api")
    app.include_router(AlbumService.to_router(), prefix="/api")

    # app.include_router(health_router, prefix="/api", tags=["health"])
    # app.include_router(upload_router, prefix="/api", tags=["upload"])

    @app.websocket(settings.WEBSOCKET_PATH)
    async def websocket_endpoint(websocket):
        await handle_websocket(websocket)

    @app.get("/")
    async def root():
        return {
            "message": "4Real FastAPI Backend",
            "version": "1.0.0",
            "docs": "/docs",
            "websocket": settings.WEBSOCKET_PATH,
            "api": "/api"
        }

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )

    return app
