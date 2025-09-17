from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from nonix_di.resolve import NxInject
from .routers.file import FileRouter
from .routers.file_category import FileCategoryRouter
from .routers.file_link import FileLinkRouter
from .routers.file_manager_router import FileManagerRouter
from .services.file_service import FileService
from .services.file_category_service import FileCategoryService
from .services.file_link_service import FileLinkService


@web_routers([
    FileRouter,
    FileCategoryRouter,
    FileLinkRouter,
    FileManagerRouter
])
@injectables([
    FileService,
    FileCategoryService,
    FileLinkService
])
class NxWebFileManagerPlugin(BasePlugin):
    file_service: FileService = NxInject(FileService)

    async def _startup(self, config: Dict[str, Any]):
        await self.file_service.initialize(config)
