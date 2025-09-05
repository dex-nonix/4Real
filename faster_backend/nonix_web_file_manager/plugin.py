from nonix_web.plugin.base_plugin import BasePlugin, routers
from nonix_web.utils.di import di_register
from .routers.file import FileRouter
from .routers.file_category import FileCategoryRouter
from .routers.file_link import FileLinkRouter
from .services.file_service import FileService
from .services.file_category_service import FileCategoryService
from .services.file_link_service import FileLinkService


@routers([
    FileRouter,
    FileCategoryRouter,
    FileLinkRouter
])
class NxWebFileManagerPlugin(BasePlugin):

    def _configure(self, server, config):
        """Register services in DI system"""
        di_register(FileService)
        di_register(FileCategoryService)
        di_register(FileLinkService)
