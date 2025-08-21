from app import create_app

# Create the Flask app and SocketIO instance for gunicorn
app, socketio = create_app()

# This is what gunicorn will import and serve
# The app object contains the Flask application
# The socketio object is attached to the app.extensions['socketio']


def start_server(host='0.0.0.0', port=5000, debug=True):
    """THE ONE FUNCTION that starts everything."""
    app, socketio = create_app()
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        # allow_unsafe_werkzeug=True
    )
    # socketio = app.extensions.get('socketio')
    # Dev static serving for uploads
    # upload_dir = app.config.get('UPLOAD_DIR')
    # if upload_dir and os.path.isdir(upload_dir):
    #     @app.route('/uploads/<path:filename>')
    #     def uploads(filename):
    #         return send_from_directory(upload_dir, filename)

    # Start the server - ONE PLACE, ONE WAY
    # if socketio:
    #     socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    # else:
    #     app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_server()
