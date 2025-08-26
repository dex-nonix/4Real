from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer


class NxWebAgenticPlugin(BasePlugin):

    async def _load_plugin(self, server: NxWebServer, config: Dict[str, Any]):
        pass
