from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from nonix_web.config import Settings
from nonix_web.plugin.plugin_manager import PluginManager


class NxWebServer(FastAPI):
    def __init__(self, settings: Settings):
        super().__init__(
            title=settings.APP_NAME,
            debug=settings.DEBUG,
            lifespan=asynccontextmanager(self._lifespan)
        )
        self.settings = settings
        self.plugin_manager = PluginManager(self, self.settings.PLUGINS.get("search_paths", "plugins"))
        self.__init__server()

    async def _setup_server(self):
        await self.plugin_manager.discover_and_load(self.settings.PLUGINS.get("plugins", []))

    async def _teardown_server(self):
        # await self.plugin_manager.unload()
        pass

    async def _lifespan(self, _):
        await self._setup_server()
        yield
        await self._teardown_server()

    def _setup_exception_handler(self):
        @self.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            return JSONResponse({"detail": f"Internal server error: {str(exc)}"}, 500)

    def __init__server(self):
        "keep for simple constructorless overload"
        ...
