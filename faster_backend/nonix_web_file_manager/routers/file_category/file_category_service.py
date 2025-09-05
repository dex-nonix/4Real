from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_file_manager.services.file_category_service import FileCategoryService


@router("/file-categories", tags=["File Categories"])
class FileCategoryRouter(NxWebServerCrudRouter):
    service: FileCategoryService = Inject(FileCategoryService)  # ✅ Just inject!
