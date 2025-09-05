from nonix_web.plugin.base_plugin import BasePlugin, routers
from .routers.file import FileRouter
from .routers.file_category import FileCategoryRouter
from .routers.file_link import FileLinkRouter


@routers([
    FileRouter,
    FileCategoryRouter,
    FileLinkRouter
])
class NxWebFileManagerPlugin(BasePlugin):
    pass
