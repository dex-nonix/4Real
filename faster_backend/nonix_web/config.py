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
        {"name": "cors"},
        {"name": "open-api"},
        {"name": "db"},
        {"name": "static-files"},
        {"name": "agentic"},
        {"name": "file-manager"},
        {"name": "music-artist"},
    ]


settings = Settings()
