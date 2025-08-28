import logging
import logging.handlers
import os
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .config import Settings
from .plugin.plugin_manager import PluginManager
from .utils.di import di_register


class NxWebServer:
    sio: socketio.AsyncServer = None
    plugin_manager: PluginManager
    app: FastAPI

    def __init__(self, settings: Settings):
        self.settings = settings
        self._setup_logging()
        self.app = FastAPI(
            title=settings.APP_NAME,
            debug=settings.DEBUG,
            lifespan=asynccontextmanager(self._lifespan),
            docs_url=None,
            redoc_url=None,
            openapi_url=None
        )
        self.plugin_manager = PluginManager(self, self.settings.PLUGIN_SEARCH_PATH)
        self.plugin_manager.discover_plugins()
        self.plugin_manager.configure_plugins(self.settings.PLUGINS)

        if settings.WS_ENABLED:
            self._enable_websocket()

        di_register(PluginManager, instance=self.plugin_manager)
        di_register(FastAPI, instance=self.app)

        self.__init__server()

    async def _lifespan(self, _):
        await self._setup_server()
        yield
        await self._teardown_server()

    async def _setup_server(self):
        await self.plugin_manager.startup_plugins(self.settings.PLUGINS)

    async def _teardown_server(self):
        await self.plugin_manager.shutdown_plugins()

    def _setup_exception_handler(self):
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            return JSONResponse({"detail": f"Internal server error: {str(exc)}"}, 500)

    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.settings.LOG_LEVEL.upper()),
            format=self.settings.LOG_FORMAT,
            datefmt=self.settings.LOG_DATE_FORMAT,
            force=True
        )
        logger = logging.getLogger()

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        if "console" in self.settings.LOG_OUTPUT:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.settings.LOG_FORMAT, self.settings.LOG_DATE_FORMAT))
            logger.addHandler(console_handler)

        if "file" in self.settings.LOG_OUTPUT:
            os.makedirs(os.path.dirname(self.settings.LOG_FILE_PATH), exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                self.settings.LOG_FILE_PATH,
                maxBytes=self.settings.LOG_MAX_SIZE,
                backupCount=self.settings.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(self.settings.LOG_FORMAT, self.settings.LOG_DATE_FORMAT))
            logger.addHandler(file_handler)

    def __init__server(self):
        "keep for simple constructorless overload"
        ...

    def _enable_websocket(self):
        self.sio = sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=self.settings.WS_ALLOWED_ORIGINS
        )
        di_register(socketio.AsyncServer, instance=sio)

        @sio.event
        async def connect(sid, environ):
            print(f"Socket.IO client connected: {sid}")

        @sio.event
        async def disconnect(sid):
            print(f"Socket.IO client disconnected: {sid}")

        @sio.on("join_room")
        async def join_room(sid, room):
            await sio.enter_room(sid, room)
            print(f"Client {sid} joined room: {room}")

        @sio.on("leave_room")
        async def join_room(sid, room):
            await sio.leave_room(sid, room)
            print(f"Client {sid} leaves room: {room}")

    @classmethod
    def run_gunicorn(cls, settings: Settings = None):
        import uvicorn
        if settings is None:
            settings = Settings()
        uvicorn.run(
            lambda: cls(settings).get_gunicorn_app(),
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL,
            factory=True
        )

    def get_gunicorn_app(self):
        if self.sio is None:
            return self.app
        return socketio.ASGIApp(self.sio, other_asgi_app=self.app)
