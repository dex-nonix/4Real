import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

# Gunicorn configuration - ALL from config
bind = Config.GUNICORN_BIND
workers = Config.GUNICORN_WORKERS
worker_class = Config.GUNICORN_WORKER_CLASS
worker_connections = Config.GUNICORN_WORKER_CONNECTIONS
max_requests = Config.GUNICORN_MAX_REQUESTS
max_requests_jitter = Config.GUNICORN_MAX_REQUESTS_JITTER
timeout = Config.GUNICORN_TIMEOUT
keepalive = Config.GUNICORN_KEEPALIVE
preload_app = Config.GUNICORN_PRELOAD_APP
worker_tmp_dir = Config.GUNICORN_WORKER_TMP_DIR
