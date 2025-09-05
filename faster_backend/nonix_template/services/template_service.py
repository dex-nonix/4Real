from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..router.template_schemas import TemplateCreate, TemplateUpdate, TemplateInDbModel
from ..models.template import Template


class TemplateService(BaseCrudService):
    """
    Internal service for template CRUD operations.
    Contains all business logic for template management.
    """
    config = CRUDConfig(
        model=Template,
        create_schema=TemplateCreate,
        update_schema=TemplateUpdate,
        response_schema=TemplateInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'description']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at', 'updated_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name', 'description']
        )
    )
