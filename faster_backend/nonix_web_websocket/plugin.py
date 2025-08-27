from typing import Dict, Any

import socketio

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer

class NxWebWebsocketPlugin(BasePlugin):
    def _configure(self, server: NxWebServer, config: Dict[str, Any]):
        sio = socketio.AsyncServer(
            cors_allowed_origins = config["cors_allowed_origins"],
            async_mode="asgi",
            logger=config["logger"],
            engineio_logger=config["engineio_logger"],
        )
        sio_app = socketio.ASGIApp(sio)
        server.mount(config["path"], sio_app)
