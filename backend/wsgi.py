from app import create_app
from flask import send_from_directory
import os

app = create_app()

# Get the SocketIO instance from the app
socketio = app.extensions.get('socketio')

# Dev static serving for uploads
upload_dir = app.config.get('UPLOAD_DIR')
if upload_dir and os.path.isdir(upload_dir):
    @app.route('/uploads/<path:filename>')
    def uploads(filename):  # pragma: no cover
        return send_from_directory(upload_dir, filename)

if __name__ == '__main__':
    # Dev run: python backend/wsgi.py
    if socketio:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)

