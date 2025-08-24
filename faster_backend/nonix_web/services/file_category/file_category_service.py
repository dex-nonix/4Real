from .file_category_schemas import FileCategoryCreate, FileCategoryUpdate, FileCategoryInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import FileCategory


@routed_service("/file_categories", tags=["File Categories"])
class FileCategoryService(GenericCRUDService):
    config = CRUDConfig(
        model=FileCategory,
        create_schema=FileCategoryCreate,
        update_schema=FileCategoryUpdate,
        response_schema=FileCategoryInDB,
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
