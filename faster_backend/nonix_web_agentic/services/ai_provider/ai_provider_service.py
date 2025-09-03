from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .ai_provider_schemas import AIProviderCreate, AIProviderUpdate, AIProviderInDbModel
from ...models.ai_provider import AIProvider


@routed_service("/ai-providers", tags=["AI Providers"])
class AIProviderService(GenericCRUDService):
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
