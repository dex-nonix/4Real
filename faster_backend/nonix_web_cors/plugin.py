from typing import Dict, Any

from fastapi.middleware.cors import CORSMiddleware

from nonix_di.resolve import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.server import NxWebServer


class NxWebCORSPlugin(BasePlugin):
    web_server: NxWebServer = NxInject(NxWebServer)

    def _configure(self, config: Dict[str, Any]):
        self.web_server.app.add_middleware(
            CORSMiddleware,
            allow_origins=config["allow_origins"],
            allow_credentials=config["allow_credentials"],
            allow_methods=config["allow_methods"],
            allow_headers=config["allow_headers"],
        )
