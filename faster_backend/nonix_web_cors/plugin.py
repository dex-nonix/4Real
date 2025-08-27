from typing import Dict, Any

from fastapi.middleware.cors import CORSMiddleware

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer



class NxWebCORSPlugin(BasePlugin):
    def _configure(self, server: NxWebServer, config: Dict[str, Any]):
        server.add_middleware(
            CORSMiddleware,
            allow_origins=config["allow_origins"],
            allow_credentials=config["allow_credentials"],
            allow_methods=config["allow_methods"],
            allow_headers=config["allow_headers"],
        )
