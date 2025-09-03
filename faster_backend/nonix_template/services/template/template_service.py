from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .template_schemas import TemplateCreate, TemplateUpdate, TemplateInDbModel
from ...models.template import Template


@routed_service("/templates", tags=["Templates"])
class TemplateService(GenericCRUDService):
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
