import logging
import logging.handlers
import os
from contextlib import asynccontextmanager
from socketio import ASGIApp

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from socketio import AsyncServer

from nonix_di.register import di_register
from nonix_plugin.manager import NxPluginManager
from .config import Settings
from .web_socket_service import NxWebServerWebSocketService


def _is_debugger_attached():
    """Checks if a debugger is attached to the current process."""
    import sys
    return sys.gettrace() is not None


def _run_server_in_process(settings: Settings):
    """Helper function that receives the settings object and runs the server."""
    NxWebServer._run_uvicorn(settings)


class NxWebServer:
    sio: AsyncServer = None
    plugin_manager: NxPluginManager
    app: FastAPI

    def __init__(self, settings: Settings):
        di_register(NxWebServer, instance=self)
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
        di_register(FastAPI, instance=self.app)
        self.plugin_manager = NxPluginManager(self.settings.PLUGIN_SEARCH_PATH)
        di_register(NxPluginManager, instance=self.plugin_manager)
        self.__init__server()
        self.plugin_manager.discover_plugins()
        self.plugin_manager.configure_plugins(self.settings.PLUGINS)

    async def _lifespan(self, _):
        await self._setup_server()
        yield
        await self._teardown_server()

    async def _setup_server(self):
        if self.settings.WS_ENABLED:
            self._enable_websocket()
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
        self.sio = sio = AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=self.settings.WS_ALLOWED_ORIGINS
        )
        di_register(AsyncServer, instance=sio)
        di_register(NxWebServerWebSocketService)

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
        async def leave_room(sid, room):
            await sio.leave_room(sid, room)
            print(f"Client {sid} leaves room: {room}")

    def get_gunicorn_app(self):
        server_ref = self

        async def dispatch(scope, receive, send):
            if server_ref.sio is None:
                return await server_ref.app(scope, receive, send)
            return await ASGIApp(server_ref.sio, other_asgi_app=server_ref.app)(scope, receive, send)

        return dispatch

    @classmethod
    def _run_uvicorn(cls, settings: Settings):
        """Internal method that contains the actual uvicorn.run call."""
        import asyncio
        import uvicorn

        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

        def run_app():
            import nest_asyncio
            nest_asyncio.apply()
            return cls(settings).get_gunicorn_app()

        uvicorn.run(
            run_app,
            host=settings.HOST,
            port=settings.PORT,
            reload=False,  # Reload must be False for debug subprocess
            log_level=settings.LOG_LEVEL,
            factory=True,
            loop="asyncio",
            ws="websockets"
        )

    @classmethod
    def run_gunicorn(cls, settings: Settings):
        if _is_debugger_attached():
            import multiprocessing
            import os

            if os.environ.get("NX_SERVER_IN_CHILD_PROCESS"):
                cls._run_uvicorn(settings)
                return

            print("✓ Debugger detected. Spawning server in a new process...")

            try:
                multiprocessing.set_start_method("spawn", force=True)
            except RuntimeError:
                pass

            os.environ["NX_SERVER_IN_CHILD_PROCESS"] = "1"

            process = multiprocessing.Process(target=_run_server_in_process, args=(settings,))
            process.start()
            try:
                process.join()
            except KeyboardInterrupt:
                process.terminate()
                process.join()
        else:
            cls._run_uvicorn(settings)
