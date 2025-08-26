from .file_category_schemas import FileCategoryCreate, FileCategoryUpdate, FileCategoryInDbModel
from nonix_web.services.base_service import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models.file_category import FileCategory


@routed_service("/file-categories", tags=["File Categories"])
class FileCategoryService(GenericCRUDService):
    config = CRUDConfig(
        model=FileCategory,
        create_schema=FileCategoryCreate,
        update_schema=FileCategoryUpdate,
        response_schema=FileCategoryInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'slug']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['slug']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name', 'slug'],
            order_by='name'
        )
    )
