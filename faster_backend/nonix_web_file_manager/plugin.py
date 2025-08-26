from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from nonix_web_file_manager.services.file import FileService
from nonix_web_file_manager.services.file_category import FileCategoryService
from nonix_web_file_manager.services.file_link import FileLinkService


class NxWebFileManagerPlugin(BasePlugin):
    api_services = [
        FileService,
        FileCategoryService,
        FileLinkService
    ]

    async def _load_plugin(self, server: NxWebServer, config: Dict[str, Any]):
        pass
