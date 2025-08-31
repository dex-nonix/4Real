from nonix_web.plugin.base_plugin import BasePlugin, api_services
from .services.file import FileService
from .services.file_category import FileCategoryService
from .services.file_link import FileLinkService


@api_services([
    FileService,
    FileCategoryService,
    FileLinkService
])
class NxWebFileManagerPlugin(BasePlugin):
    pass
