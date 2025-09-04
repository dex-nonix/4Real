from nonix_web.router.web_server_router import router
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .ai_provider_schemas import AIProviderCreate, AIProviderUpdate, AIProviderInDbModel
from ...models.ai_provider import AIProvider


@router("/ai-providers", tags=["AI Providers"])
class AIProviderRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=AIProvider,
        create_schema=AIProviderCreate,
        update_schema=AIProviderUpdate,
        response_schema=AIProviderInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'provider_type', 'module', 'cls', 'method', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'provider_type', 'module', 'cls', 'method', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name', 'provider_type', 'module', 'cls', 'method'],
            display_format='{name}',
            search_fields=['name', 'provider_type', 'module', 'cls']
        )
    )
