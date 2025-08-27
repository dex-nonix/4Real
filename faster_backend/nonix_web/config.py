class Settings:
    APP_NAME: str = "NxWebServer"
    DEBUG: bool = False
    LOG_LEVEL: str = "info"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_OUTPUT: list = ["console"]
    LOG_FILE_PATH: str = "logs/server.log"
    LOG_MAX_SIZE: int = 10485760
    LOG_BACKUP_COUNT: int = 5
    WS_ENABLED=True
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    PLUGIN_SEARCH_PATH = [
        "plugins"
        # "./"
    ]
    PLUGINS = []
