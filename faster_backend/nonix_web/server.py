from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .config import Settings, settings as _settings
from .plugin.plugin_manager import PluginManager


@asynccontextmanager
async def _lifespan(self):
    await self._setup_server()
    yield
    await self._teardown_server()


class NxWebServer(FastAPI):
    def __init__(self, settings: Settings = _settings):
        super().__init__(
            title=settings.APP_NAME,
            debug=settings.DEBUG,
            lifespan=_lifespan
        )
        self.settings = settings
        self.plugin_manager = PluginManager(self, self.settings.PLUGIN_SEARCH_PATH)
        self.plugin_manager.discover_plugins()
        self.plugin_manager.configure_plugins(self.settings.PLUGINS)
        self.__init__server()

    async def _setup_server(self):
        await self.plugin_manager.startup_plugins(self.settings.PLUGINS)

    async def _teardown_server(self):
        await self.plugin_manager.shutdown_plugins()

    def _setup_exception_handler(self):
        @self.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            return JSONResponse({"detail": f"Internal server error: {str(exc)}"}, 500)

    def __init__server(self):
        "keep for simple constructorless overload"
        ...

    @classmethod
    def run_gunicorn(cls, settings: Settings = _settings):
        import uvicorn
        uvicorn.run(
            lambda: cls(settings),
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL,
            factory=True
        )
