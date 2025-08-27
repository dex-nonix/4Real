if __name__ == "__main__":
    from nonix_web.config import Settings
    from nonix_web.server import NxWebServer

    settings = Settings()
    # settings.DEBUG = True
    settings.PLUGIN_SEARCH_PATH = ["./"]
    settings.PLUGINS = [
        {"name": "cors"},
        {"name": "open-api"},
        {"name": "db"},
        {"name": "static-files"},
        {"name": "agentic"},
        # {"name": "websocket"},
        # {"name": "file-manager"}, # settings problem
        {"name": "music-artist"},
    ]

    NxWebServer.run_gunicorn(settings)
