import json
import logging
import os
import sys
import traceback

from dotenv import load_dotenv
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy

from .api_router.api_router import APIRouter

db = SQLAlchemy()


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    
    # Load config FIRST
    app.config.from_object('config.Config')
    
    # Configure logging based on config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    if app.config.get('DEBUG'):
        # Development logging with colors
        logging.basicConfig(
            level=log_level,
            format=app.config.get('LOG_FORMAT'),
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(app.config.get('LOG_FILE'))
            ]
        )
        
        # Force immediate output (no buffering)
        for handler in logging.root.handlers:
            handler.setFormatter(logging.Formatter(
                '\033[1m%(asctime)s\033[0m [\033[91m%(levelname)s\033[0m] \033[94m%(name)s\033[0m: %(message)s'
            ))
            handler.flush = lambda: None  # Force immediate flush
    else:
        # Production logging
        logging.basicConfig(
            level=log_level,
            format=app.config.get('LOG_FORMAT'),
            handlers=[
                logging.FileHandler(app.config.get('LOG_FILE'))
            ]
        )

    app.logger.setLevel(log_level)

    # Initialize CORS with config
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Initialize database with config
    db.init_app(app)

    # Initialize Flask-SocketIO with config - using asyncio mode
    socketio = SocketIO(
        async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'asyncio'),
        cors_allowed_origins=app.config.get('SOCKETIO_CORS_ORIGINS', '*'),
        logger=app.config.get('SOCKETIO_LOGGER', False),
        engineio_logger=app.config.get('SOCKETIO_ENGINE_LOGGER', False),
        path=app.config.get('SOCKETIO_PATH', '/api/ws')
    )
    socketio.init_app(app)


    @socketio.on('connect')
    def handle_connect():
        print("----------------------------- WS CONNECT ")
        app.logger.info(f"WebSocket client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        print("-----------------------------WS DISCONNECT")
        app.logger.info(f"WebSocket client disconnected: {request.sid}")

    @socketio.on('join')
    def handle_join_room(room):
        print("-----------------------------WS JOIN")
        if room:
            app.logger.info(f"DEBUG: Attempting to join room '{room}' for client {request.sid}")
            join_room(room)

    @socketio.on('leave')
    def handle_leave_room(room):
        print("-----------------------------WS LEAVE")
        if room:
            leave_room(room)
            app.logger.info(f"Client {request.sid} left room: {room}")
        else:
            app.logger.warning(f"Client {request.sid} tried to leave room but no room specified")

    app.extensions['socketio'] = socketio

    app.logger.info("WebSocket event handlers registered successfully!")

    # COMPREHENSIVE ERROR HANDLING - Catch everything!

    # 1. Global exception handler for ALL unhandled exceptions
    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        app.logger.error(f"💥 UNHANDLED EXCEPTION: {type(e).__name__}: {str(e)}", exc_info=True)

        return jsonify({
            'error': 'Internal Server Error',
            'exception_type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
        }), 500

    # 2. Specific HTTP error handlers
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"🔥 500 Internal Server Error: {error}", exc_info=True)

        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error),
            'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
        }), 500

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"⚠️  404 Not Found: {request.url}")
        return jsonify({
            'error': 'Not Found',
            'message': f'The requested URL {request.url} was not found'
        }), 404

    # 3. Database error handler
    @app.errorhandler(Exception)
    def handle_database_errors(e):
        if 'database' in str(e).lower() or 'sql' in str(e).lower() or 'db' in str(e).lower():
            app.logger.error(f"🗄️  DATABASE ERROR: {type(e).__name__}: {str(e)}", exc_info=True)

            return jsonify({
                'error': 'Database Error',
                'exception_type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
            }), 500
        return None  # Let other handlers deal with it

    # 4. WebSocket event handlers - Will be registered after APIRouter initialization

    # Initialize APIRouter with SocketIO instance
    api_router = APIRouter(socketio_instance=socketio)

    with app.app_context():
        try:
            app.logger.info("Initializing database and services...")

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
            from .services.chat_history_service import ChatHistoryService

            from .services.tool_invocation_log_service import ToolInvocationLogService
            from .services.chat_service import ChatService
            from .services.file_category_service import FileCategoryService
            from .services.file_service import FileService
            from .services.file_link_service import FileLinkService

            app.logger.info("Registering services...")

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
            api_router.register_service('chat-histories', ChatHistoryService)
            api_router.register_service('tool-invocation-logs', ToolInvocationLogService)
            api_router.register_service('chat', ChatService, app=app)
            api_router.register_service('file-categories', FileCategoryService)
            api_router.register_service('files', FileService)
            api_router.register_service('file-links', FileLinkService)



            app.logger.info("Creating database tables...")
            db.create_all()

            # Serve uploaded files directly from the API server in all run modes
            upload_dir = app.config.get('UPLOAD_DIR')
            if upload_dir and os.path.isdir(upload_dir):
                @app.route('/uploads/<path:filename>')
                def uploads(filename):  # pragma: no cover
                    return send_from_directory(upload_dir, filename)

            app.logger.info("All services and database initialized successfully!")

        except Exception as e:
            app.logger.error(f"💥 CRITICAL ERROR during app initialization: {type(e).__name__}: {str(e)}", exc_info=True)
            raise  # Re-raise to prevent silent failures

    # Add error handling to all blueprint registrations
    def register_blueprint_with_error_handling(blueprint, **kwargs):
        """Register blueprint with comprehensive error handling"""
        try:
            app.register_blueprint(blueprint, **kwargs)
            app.logger.info(f"Successfully registered blueprint: {blueprint.name}")
        except Exception as e:
            app.logger.error(f"💥 FAILED to register blueprint {blueprint.name}: {str(e)}", exc_info=True)
            raise  # Re-raise to prevent silent failures

    # Register the API router with error handling
    register_blueprint_with_error_handling(api_router.blueprint, url_prefix='/api')

    # Register SocketIO with the Flask app
    # socketio.init_app(app)

    app.logger.info("Flask app initialized successfully with comprehensive error logging")

    # FINAL SAFETY NET - Catch ALL errors at WSGI level
    class ErrorCatchingMiddleware:
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            try:
                return self.app(environ, start_response)
            except Exception as e:
                # This catches ANY error that wasn't caught by Flask handlers
                app.logger.error(f"🚨 WSGI LEVEL CRASH: {type(e).__name__}: {str(e)}", exc_info=True)

                # Return error response
                status = '500 Internal Server Error'
                response_headers = [('Content-type', 'application/json')]
                start_response(status, response_headers)
                return [json.dumps({
                    'error': 'WSGI Level Error',
                    'exception_type': type(e).__name__,
                    'message': str(e),
                    'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
                }).encode('utf-8')]

    # Wrap the app with our error-catching middleware
    app.wsgi_app = ErrorCatchingMiddleware(app.wsgi_app)

    # Dev static serving for uploads
    upload_dir = app.config.get('UPLOAD_DIR')
    if upload_dir and os.path.isdir(upload_dir):
        @app.route('/uploads/<path:filename>')
        def uploads(filename):
            return send_from_directory(upload_dir, filename)



    return app, socketio
