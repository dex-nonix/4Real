from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from nonix_di.decorator import injectables
from .routers.file import FileRouter
from .routers.file_category import FileCategoryRouter
from .routers.file_link import FileLinkRouter
from .services.file_category_service import FileCategoryService
from .services.file_link_service import FileLinkService
from .services.file_service import FileService


@web_routers([
    FileRouter,
    FileCategoryRouter,
    FileLinkRouter
])
@injectables([
    FileService,
    FileCategoryService,
    FileLinkService
])
class NxWebFileManagerPlugin(BasePlugin):
    pass
