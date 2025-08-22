from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "4Real FastAPI Backend"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/4real_db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30

    # File Uploads
    UPLOAD_FOLDER: str = "static/uploads"
    STATIC_URL_PREFIX: str = "/static/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".md", ".xml"]

    # WebSocket
    WEBSOCKET_PATH: str = "/ws"
    WEBSOCKET_MAX_CONNECTIONS: int = 1000

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
