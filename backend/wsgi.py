from app import create_app
from flask import send_from_directory
import os

def start_server(host='0.0.0.0', port=5000, debug=True):
    """THE ONE FUNCTION that starts everything."""
    app = create_app()
    socketio = app.extensions.get('socketio')
    
    # Dev static serving for uploads
    upload_dir = app.config.get('UPLOAD_DIR')
    if upload_dir and os.path.isdir(upload_dir):
        @app.route('/uploads/<path:filename>')
        def uploads(filename):
            return send_from_directory(upload_dir, filename)
    
    # Start the server - ONE PLACE, ONE WAY
    if socketio:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    else:
        app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_server()

