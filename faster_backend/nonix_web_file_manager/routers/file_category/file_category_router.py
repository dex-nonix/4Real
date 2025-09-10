from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from nonix_web_file_manager.services.file_category_service import FileCategoryService


@router("/file-categories", tags=["File Categories"])
class FileCategoryRouter(NxWebServerCrudRouter):
    service: FileCategoryService = NxInject(FileCategoryService)  # ✅ Just inject!
