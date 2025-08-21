import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'app.db')

    # Environment detection
    ENV = os.getenv('FLASK_ENV', 'development')
    PRODUCTION = ENV == 'production'
    DEBUG = not PRODUCTION and os.getenv('FLASK_DEBUG', '1') == '1'

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'flask_errors.log')

    # WebSocket
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'threading')
    SOCKETIO_CORS_ORIGINS = os.getenv('SOCKETIO_CORS_ORIGINS', CORS_ORIGINS)
    SOCKETIO_LOGGER = os.getenv('SOCKETIO_LOGGER', str(DEBUG)).lower() == 'true'
    SOCKETIO_ENGINE_LOGGER = os.getenv('SOCKETIO_ENGINE_LOGGER', str(DEBUG)).lower() == 'true'
    SOCKETIO_PATH = os.getenv('SOCKETIO_PATH', '/api/ws')

    # Gunicorn - ALL SETTINGS HERE
    GUNICORN_BIND = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')
    GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', '4'))
    GUNICORN_WORKER_CLASS = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
    GUNICORN_WORKER_CONNECTIONS = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))
    GUNICORN_MAX_REQUESTS = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
    GUNICORN_MAX_REQUESTS_JITTER = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '100'))
    GUNICORN_TIMEOUT = int(os.getenv('GUNICORN_TIMEOUT', '30'))
    GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', '2'))
    GUNICORN_PRELOAD_APP = os.getenv('GUNICORN_PRELOAD_APP', 'true').lower() == 'true'
    GUNICORN_WORKER_TMP_DIR = os.getenv('GUNICORN_WORKER_TMP_DIR', '/dev/shm')

    # Uploads (dev)
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(BASE_DIR, 'uploads'))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(50 * 1024 * 1024)))  # 50MB default
    # Public base URL for building absolute file URLs (e.g., https://api.example.com)
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '')

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
