from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from .services.file import FileService
from .services.file_category import FileCategoryService
from .services.file_link import FileLinkService


class NxWebFileManagerPlugin(BasePlugin):
    api_services = [
        FileService,
        FileCategoryService,
        FileLinkService
    ]