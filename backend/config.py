import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'app.db')

    # Allow overriding via environment
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Flask env
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'

    # Uploads (dev)
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(BASE_DIR, 'uploads'))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(50 * 1024 * 1024)))  # 50MB default
    # Public base URL for building absolute file URLs (e.g., https://api.example.com)
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '')
