from typing import Dict, Any

from fastapi.staticfiles import StaticFiles

from nonix_di import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.server import NxWebServer


class NxWebStaticFilesPlugin(BasePlugin):
    web_server: NxWebServer = NxInject(NxWebServer)

    def _configure(self, config: Dict[str, Any]):
        self.web_server.app.mount(
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
