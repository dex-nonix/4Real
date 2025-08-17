from flask import Flask, send_from_directory, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import traceback
import sys
from werkzeug.exceptions import HTTPException


db = SQLAlchemy()


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Configure aggressive logging with colors and immediate output
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('flask_errors.log')  # Also log to file
        ]
    )
    
    # Force immediate output (no buffering)
    for handler in logging.root.handlers:
        handler.setFormatter(logging.Formatter(
            '\033[1m%(asctime)s\033[0m [\033[91m%(levelname)s\033[0m] \033[94m%(name)s\033[0m: %(message)s'
        ))
        handler.flush = lambda: None  # Force immediate flush
    
    app.logger.setLevel(logging.DEBUG)
    
    # Make sure errors are immediately visible
    def log_error_and_exit(msg, *args, **kwargs):
        print(f"\n\033[91m🔥 CRITICAL ERROR 🔥\033[0m: {msg}", file=sys.stderr)
        sys.stderr.flush()
        # Don't call app.logger.error again - this prevents infinite recursion
        # app.logger.error(msg, *args, **kwargs)
    
    # Don't replace the logger's error method - this causes infinite recursion
    # app.logger.error = log_error_and_exit

    CORS(app)
    db.init_app(app)

    # COMPREHENSIVE ERROR HANDLING - Catch everything!
    
    # 1. Global exception handler for ALL unhandled exceptions
    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        error_msg = f"💥 UNHANDLED EXCEPTION: {type(e).__name__}: {str(e)}"
        traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
        
        # Print immediately to terminal
        print(f"\n{error_msg}", file=sys.stderr)
        print(f"{traceback_msg}", file=sys.stderr)
        sys.stderr.flush()
        
        # Also log normally
        app.logger.error(error_msg)
        app.logger.error(traceback_msg)
        
        return jsonify({
            'error': 'Internal Server Error',
            'exception_type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
        }), 500

    # 2. Specific HTTP error handlers
    @app.errorhandler(500)
    def internal_error(error):
        error_msg = f"🔥 500 Internal Server Error: {error}"
        traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
        
        # Print immediately to terminal
        print(f"\n{error_msg}", file=sys.stderr)
        print(f"{traceback_msg}", file=sys.stderr)
        sys.stderr.flush()
        
        # Also log normally
        app.logger.error(error_msg)
        app.logger.error(traceback_msg)
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error),
            'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
        }), 500

    @app.errorhandler(404)
    def not_found_error(error):
        warning_msg = f"⚠️  404 Not Found: {request.url}"
        print(f"\n{warning_msg}", file=sys.stderr)
        sys.stderr.flush()
        app.logger.warning(warning_msg)
        return jsonify({
            'error': 'Not Found',
            'message': f'The requested URL {request.url} was not found'
        }), 404

    # 3. Database error handler
    @app.errorhandler(Exception)
    def handle_database_errors(e):
        if 'database' in str(e).lower() or 'sql' in str(e).lower() or 'db' in str(e).lower():
            error_msg = f"🗄️  DATABASE ERROR: {type(e).__name__}: {str(e)}"
            traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
            
            # Print immediately to terminal
            print(f"\n{error_msg}", file=sys.stderr)
            print(f"{traceback_msg}", file=sys.stderr)
            sys.stderr.flush()
            
            # Also log normally
            app.logger.error(error_msg)
            app.logger.error(traceback_msg)
            
            return jsonify({
                'error': 'Database Error',
                'exception_type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
            }), 500
        return None  # Let other handlers deal with it

    # 4. Request logging middleware with immediate output
    @app.before_request
    def log_request_info():
        request_msg = f"📥 Request: {request.method} {request.url}"
        print(f"\n{request_msg}")
        sys.stdout.flush()
        app.logger.info(request_msg)
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = request.get_json(silent=True)
            if data:
                data_msg = f"📦 Request data: {data}"
                print(f"{data_msg}")
                sys.stdout.flush()
                app.logger.debug(data_msg)

    @app.after_request
    def log_response_info(response):
        status_color = '\033[92m' if response.status_code < 400 else '\033[91m'
        response_msg = f"📤 Response: {status_color}{response.status_code}\033[0m for {request.method} {request.url}"
        print(f"{response_msg}")
        sys.stdout.flush()
        app.logger.info(response_msg)
        return response

    # 5. Add error handling to all blueprint registrations
    def register_blueprint_with_error_handling(blueprint, **kwargs):
        """Register blueprint with comprehensive error handling"""
        try:
            app.register_blueprint(blueprint, **kwargs)
            print(f"✅ Successfully registered blueprint: {blueprint.name}")
            sys.stdout.flush()
        except Exception as e:
            error_msg = f"💥 FAILED to register blueprint {blueprint.name}: {str(e)}"
            traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
            
            print(f"\n{error_msg}", file=sys.stderr)
            print(f"{traceback_msg}", file=sys.stderr)
            sys.stderr.flush()
            
            app.logger.error(error_msg)
            app.logger.error(traceback_msg)
            raise  # Re-raise to prevent silent failures

    from .api_router import APIRouter
    api_router = APIRouter()

    with app.app_context():
        try:
            print("🚀 Initializing database and services...")
            sys.stdout.flush()
            
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

            print("📋 Registering services...")
            sys.stdout.flush()

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
            api_router.register_service('chat', ChatService)
            api_router.register_service('file-categories', FileCategoryService)
            api_router.register_service('files', FileService)
            api_router.register_service('file-links', FileLinkService)

            print("🗄️  Creating database tables...")
            sys.stdout.flush()
            db.create_all()

            # Serve uploaded files directly from the API server in all run modes
            upload_dir = app.config.get('UPLOAD_DIR')
            if upload_dir and os.path.isdir(upload_dir):
                @app.route('/uploads/<path:filename>')
                def uploads(filename):  # pragma: no cover
                    return send_from_directory(upload_dir, filename)

            print("✅ All services and database initialized successfully!")
            sys.stdout.flush()
            
        except Exception as e:
            error_msg = f"💥 CRITICAL ERROR during app initialization: {type(e).__name__}: {str(e)}"
            traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
            
            print(f"\n{error_msg}", file=sys.stderr)
            print(f"{traceback_msg}", file=sys.stderr)
            sys.stderr.flush()
            
            app.logger.error(error_msg)
            app.logger.error(traceback_msg)
            raise  # Re-raise to prevent silent failures

    # Register the API router with error handling
    register_blueprint_with_error_handling(api_router.blueprint, url_prefix='/api')
    
    # Test endpoint to verify error logging
    @app.route('/test-error')
    def test_error():
        """Test endpoint to verify error logging is working"""
        print("\n🧪 Testing error logging...")
        sys.stdout.flush()
        app.logger.info("Testing error logging...")
        raise Exception("This is a test error to verify logging is working!")
    
    print("\n✅ Flask app initialized successfully with COMPREHENSIVE error logging!")
    sys.stdout.flush()
    app.logger.info("Flask app initialized successfully")
    
    # FINAL SAFETY NET - Catch ALL errors at WSGI level
    class ErrorCatchingMiddleware:
        def __init__(self, app):
            self.app = app
        
        def __call__(self, environ, start_response):
            try:
                return self.app(environ, start_response)
            except Exception as e:
                # This catches ANY error that wasn't caught by Flask handlers
                error_msg = f"🚨 WSGI LEVEL CRASH: {type(e).__name__}: {str(e)}"
                traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
                
                # Print immediately to terminal
                print(f"\n{error_msg}", file=sys.stderr)
                print(f"{traceback_msg}", file=sys.stderr)
                sys.stderr.flush()
                
                # Also log normally
                app.logger.error(error_msg)
                app.logger.error(traceback_msg)
                
                # Return error response
                status = '500 Internal Server Error'
                response_headers = [('Content-type', 'application/json')]
                start_response(status, response_headers)
                return [jsonify({
                    'error': 'WSGI Level Error',
                    'exception_type': type(e).__name__,
                    'message': str(e),
                    'traceback': traceback.format_exc() if app.config.get('DEBUG') else None
                }).get_data()]
    
    # Wrap the app with our error-catching middleware
    app.wsgi_app = ErrorCatchingMiddleware(app.wsgi_app)
    
    return app

