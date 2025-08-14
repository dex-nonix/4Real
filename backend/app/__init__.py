from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv


db = SQLAlchemy()


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('config.Config')

    CORS(app)
    db.init_app(app)

    from .services.api_router import APIRouter
    api_router = APIRouter()

    with app.app_context():
        # Register services with the APIRouter
        from .services.artist_service import ArtistService
        from .services.album_service import AlbumService
        from .services.track_service import TrackService
        from .services.style_service import StyleService
        from .services.rhyme_technique_service import RhymeTechniqueService
        from .services.ai_provider_service import AIProviderService
        from .services.ai_model_mapping_service import AIModelMappingService
        from .services.ai_analysis_result_service import AIAnalysisResultService
        from .services.persona_service import PersonaService
        from .services.internal_tool_service import InternalToolService
        from .services.persona_tool_access_service import PersonaToolAccessService
        from .services.mcp_server_service import MCPServerService
        from .services.persona_mcp_server_service import PersonaMCPServerService
        from .services.chat_session_service import ChatSessionService
        from .services.chat_message_service import ChatMessageService
        from .services.tool_invocation_log_service import ToolInvocationLogService
        from .services.chat_service import ChatService
        from .services.file_category_service import FileCategoryService
        from .services.file_service import FileService
        from .services.file_link_service import FileLinkService

        api_router.register_service('artists', ArtistService)
        api_router.register_service('albums', AlbumService)
        api_router.register_service('tracks', TrackService)
        api_router.register_service('styles', StyleService)
        api_router.register_service('rhyme-techniques', RhymeTechniqueService)
        api_router.register_service('ai-providers', AIProviderService)
        api_router.register_service('ai-model-mappings', AIModelMappingService)
        api_router.register_service('ai-analysis-results', AIAnalysisResultService)
        api_router.register_service('personas', PersonaService)
        api_router.register_service('internal-tools', InternalToolService)
        api_router.register_service('persona-tool-access', PersonaToolAccessService)
        api_router.register_service('mcp-servers', MCPServerService)
        api_router.register_service('persona-mcp-servers', PersonaMCPServerService)
        api_router.register_service('chat-sessions', ChatSessionService)
        api_router.register_service('chat-messages', ChatMessageService)
        api_router.register_service('tool-invocation-logs', ToolInvocationLogService)
        api_router.register_service('chat', ChatService)
        api_router.register_service('file-categories', FileCategoryService)
        api_router.register_service('files', FileService)
        api_router.register_service('file-links', FileLinkService)

        db.create_all()

    app.register_blueprint(api_router.blueprint, url_prefix='/api')
    return app

