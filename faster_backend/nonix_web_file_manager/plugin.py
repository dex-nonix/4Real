from nonix_web.plugin.base_plugin import BasePlugin, routers, services
from .routers.file import FileRouter
from .routers.file_category import FileCategoryRouter
from .routers.file_link import FileLinkRouter
from .services.file_category_service import FileCategoryService
from .services.file_link_service import FileLinkService
from .services.file_service import FileService


@routers([
    FileRouter,
    FileCategoryRouter,
    FileLinkRouter
])
@services([
    FileService,
    FileCategoryService,
    FileLinkService
])
class NxWebFileManagerPlugin(BasePlugin):
    pass
