from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.di import Inject
from nonix_web_file_manager.services.file_link_service import FileLinkService


@router("/file-links", tags=["File Links"])
class FileLinkRouter(NxWebServerCrudRouter):
    service: FileLinkService = Inject(FileLinkService)  # ✅ Just inject!
