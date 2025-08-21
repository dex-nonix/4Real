import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

# Flask-SocketIO specific settings for gevent websockets
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'

# Gunicorn configuration - ALL from config
bind = Config.GUNICORN_BIND
workers = Config.GUNICORN_WORKERS
worker_connections = Config.GUNICORN_WORKER_CONNECTIONS
max_requests = Config.GUNICORN_MAX_REQUESTS
max_requests_jitter = Config.GUNICORN_MAX_REQUESTS_JITTER
timeout = Config.GUNICORN_TIMEOUT
keepalive = Config.GUNICORN_KEEPALIVE
preload_app = Config.GUNICORN_PRELOAD_APP
worker_tmp_dir = Config.GUNICORN_WORKER_TMP_DIR

# Environment variables for Flask-SocketIO
raw_env = [
    f"FLASK_ENV={os.getenv('FLASK_ENV', 'production')}",
    f"FLASK_DEBUG={os.getenv('FLASK_DEBUG', '0')}",
    f"LOG_LEVEL={os.getenv('LOG_LEVEL', 'INFO')}",
    f"SOCKETIO_LOGGER={os.getenv('SOCKETIO_LOGGER', 'false')}",
    f"SOCKETIO_ENGINE_LOGGER={os.getenv('SOCKETIO_ENGINE_LOGGER', 'false')}"
]
