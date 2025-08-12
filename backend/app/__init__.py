from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object('backend.config.Config')

    # Extensions
    CORS(app)
    db.init_app(app)

    # Blueprint router
    from .services.api_router import APIRouter
    api_router = APIRouter()

    with app.app_context():
        # Import models so they are registered with SQLAlchemy
        from .models.artist import Artist  # noqa: F401

        # Create tables on startup for MVP
        db.create_all()

        # Register services (no dependencies needed for MVP)
        from .services.artist_service import ArtistService
        api_router.register_service('artists', ArtistService)

    app.register_blueprint(api_router.blueprint, url_prefix='/api')
    return app

