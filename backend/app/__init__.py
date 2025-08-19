from flask import Flask, send_from_directory, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import re
import os
import logging
import traceback
import sys
from werkzeug.exceptions import HTTPException

from .api_router.api_router import APIRouter


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
    
    CORS(app)
    db.init_app(app)

    # Initialize Flask-SocketIO for WebSocket support
    from flask_socketio import SocketIO
    socketio = SocketIO(app, 
        cors_allowed_origins="*", 
        logger=True, 
        engineio_logger=True,
        path='/api/ws'  # SocketIO server runs on /api/ws path
    )
    
    # Make SocketIO available as app extension
    app.extensions['socketio'] = socketio

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

    # 4. WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        print(f"🔌 WebSocket client connected: {request.sid}")
        app.logger.info(f"WebSocket client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"🔌 WebSocket client disconnected: {request.sid}")
        app.logger.info(f"WebSocket client disconnected: {request.sid}")

    @socketio.on('join_channel')
    def handle_join_channel(data):
        """Handle client joining a specific channel."""
        channel = data.get('channel')
        if channel:
            from flask_socketio import join_room
            join_room(channel)
            print(f"🔌 Client {request.sid} joined channel: {channel}")
            app.logger.info(f"Client {request.sid} joined channel: {channel}")
            return {'status': 'success', 'channel': channel}
        return {'status': 'error', 'message': 'No channel specified'}

    @socketio.on('channel_message')
    def handle_channel_message(data):
        """Route incoming channel messages to appropriate @expose_ws methods."""
        channel = data.get('channel')
        message_data = data.get('data')
        
        if not channel or not message_data:
            return {'error': 'Missing channel or data'}
        
        # Get the APIRouter instance to find WebSocket methods
        from .api_router.api_router import APIRouter
        router = APIRouter.get_instance()
        
        if router:
            websocket_channels = router.get_websocket_channels()
            
            # Find which @expose_ws method handles this channel
            for registered_channel, channel_info in websocket_channels.items():
                if channel_matches(registered_channel, channel):
                    service = channel_info['service']
                    method_name = channel_info['method_name']
                    method = getattr(service, method_name)
                    
                    try:
                        # Extract path parameters from channel
                        params = extract_channel_params(registered_channel, channel)
                        
                        # Call the service method with extracted parameters
                        result = method(message_data, **params)
                        return {'status': 'success', 'result': result}
                    except Exception as e:
                        app.logger.error(f"WebSocket method execution error: {str(e)}")
                        return {'error': str(e)}
            
            return {'error': 'Channel not found'}
        
        return {'error': 'Router not available'}

    def channel_matches(pattern: str, channel: str) -> bool:
        """Check if a channel matches a pattern with placeholders."""
        # Convert pattern placeholders to regex
        # {param} -> ([^/]+)
        regex_pattern = re.sub(r'\{([^}]+)\}', r'([^/]+)', pattern)
        
        # Add start/end anchors
        regex_pattern = f'^{regex_pattern}$'
        
        # Check if channel matches pattern
        return bool(re.match(regex_pattern, channel))

    def extract_channel_params(pattern: str, channel: str) -> dict:
        """Extract parameters from channel based on pattern."""
        params = {}
        
        # Find all placeholders in pattern
        placeholders = re.findall(r'\{([^}]+)\}', pattern)
        
        # Convert pattern to regex for extraction
        regex_pattern = re.sub(r'\{([^}]+)\}', r'([^/]+)', pattern)
        regex_pattern = f'^{regex_pattern}$'
        
        # Extract values
        match = re.match(regex_pattern, channel)
        if match:
            for i, placeholder in enumerate(placeholders):
                params[placeholder] = match.group(i + 1)
        
        return params

    # Initialize APIRouter with SocketIO instance
    api_router = APIRouter(socketio_instance=socketio)

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

    # Add error handling to all blueprint registrations
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

    # Register the API router with error handling
    register_blueprint_with_error_handling(api_router.blueprint, url_prefix='/api')
    
    # Register SocketIO with the Flask app
    socketio.init_app(app)
    
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

