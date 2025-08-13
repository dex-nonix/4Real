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

        api_router.register_service('artists', ArtistService)
        api_router.register_service('albums', AlbumService)
        api_router.register_service('tracks', TrackService)
        api_router.register_service('styles', StyleService)
        api_router.register_service('rhyme-techniques', RhymeTechniqueService)
        api_router.register_service('ai-providers', AIProviderService)
        api_router.register_service('ai-model-mappings', AIModelMappingService)
        api_router.register_service('ai-analysis-results', AIAnalysisResultService)

        db.create_all()

    app.register_blueprint(api_router.blueprint, url_prefix='/api')
    return app

