class Settings:
    APP_NAME: str = "NxWebServer"
    DEBUG: bool = False
    LOG_LEVEL: str = "debug"
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    PLUGIN_SEARCH_PATH = [
        "plugins"
        # "./"
    ]
    PLUGINS = []
