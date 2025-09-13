if __name__ == "__main__":
    from nonix_web.config import Settings
    from nonix_web.server import NxWebServer

    settings = Settings()
    settings.PLUGIN_SEARCH_PATH = ["./"]
    settings.LOG_LEVEL = "debug"
    settings.PLUGINS = [
        {"name": "cors"},
        {"name": "open-api"},
        {"name": "db"},
        {"name": "template"},
        {"name": "static-files"},
        {"name": "agentic"},
        {"name": "file-manager"},
        {"name": "music-artist"},

    ]

    NxWebServer.run_gunicorn(settings)
