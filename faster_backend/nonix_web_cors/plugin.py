from typing import Dict, Any

from fastapi.middleware.cors import CORSMiddleware

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer

_ALLOW_ALL = ["*"]

class NxWebCORSPlugin(BasePlugin):

    async def configure(self, server: NxWebServer, config: Dict[str, Any]):
        server.add_middleware(
            CORSMiddleware,
            allow_origins=config.get("origins", _ALLOW_ALL),
            allow_credentials=config.get("allow_credentials", True),
            allow_methods=config.get("allow_methods", _ALLOW_ALL),
            allow_headers=config.get("allow_headers", _ALLOW_ALL),
        )
