from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .internal_tool_schemas import InternalToolCreate, InternalToolUpdate, InternalToolInDbModel
from ...models.internal_tool import InternalTool


@routed_service("/internal-tools", tags=["Internal Tools"])
class InternalToolRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=InternalTool,
        create_schema=InternalToolCreate,
        update_schema=InternalToolUpdate,
        response_schema=InternalToolInDbModel,
        filters=FilterConfig(
            allowed_fields=['namespace', 'name', 'qualified_name', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='qualified_name',
            allowed_fields=['namespace', 'name', 'qualified_name', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['qualified_name']
        ),
        selector=SelectorConfig(
            fields=['qualified_name', 'name', 'namespace'],
            display_format='{qualified_name}',
            search_fields=['qualified_name', 'name', 'namespace']
        )
    )
