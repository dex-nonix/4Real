from typing import List

from sqlalchemy.pool.impl import NullPool

DEV_MODE = True


class Settings:
    APP_NAME: str = "4Real FastAPI Backend"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    PLUGIN_SEARCH_PATH = [
        # "plugins"
        "./"
    ]
    PLUGINS = [
        {"name":"cors"},
        {"name":"openapi"},
        {"name":"db"},
        {"name":"static-files"},
        {"name": "agentic"},
        {"name": "file-manager"},
        {"name": "music-artist"},
    ]

    # # CORS
    # CORS_ORIGINS: List[str] = ["*"]
    # CORS_ALLOW_CREDENTIALS: bool = True
    # CORS_ALLOW_METHODS: List[str] = ["*"]
    # CORS_ALLOW_HEADERS: List[str] = ["*"]
    #
    # # Database
    # if DEV_MODE:
    #     DATABASE_URL: str = "sqlite+aiosqlite:///./4real.db"
    #     DATABASE_OPTIONS = dict(
    #         echo=True,
    #         poolclass=NullPool if DEBUG else None,
    #     )
    # else:
    #     DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/4real_db"
    #     DATABASE_OPTIONS = dict(
    #         echo=True,
    #         poolclass=NullPool if DEBUG else None,
    #         pool_size=20,
    #         max_overflow=30,
    #     )
    #
    # # File Uploads
    # UPLOAD_FOLDER: str = "static/uploads"
    # STATIC_URL_PREFIX: str = "./static/uploads"
    # MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    # ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".md", ".xml"]
    #
    # # Security
    # SECRET_KEY: str = "your-secret-key-here-change-in-production"
    #
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True
    #

settings = Settings()
