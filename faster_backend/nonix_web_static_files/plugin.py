from typing import Dict, Any

from fastapi.staticfiles import StaticFiles

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer


class NxWebStaticFilesPlugin(BasePlugin):

    async def configure(self, server: NxWebServer, config: Dict[str, Any]):
        server.mount(
            config["path"],
            StaticFiles(
                directory=config["directory"],
                packages=config["packages"],
                html=config["html"],
                check_dir=config["check_dir"],
                follow_symlink=config["follow_symlink"],
            ),
            name=config["name"],
        )
