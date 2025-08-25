from .ai_provider_schemas import AIProviderCreate, AIProviderUpdate, AIProviderInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import AIProvider


@routed_service("/ai-providers", tags=["AI Providers"])
class AIProviderService(GenericCRUDService):
    config = CRUDConfig(
        model=AIProvider,
        create_schema=AIProviderCreate,
        update_schema=AIProviderUpdate,
        response_schema=AIProviderInDB,
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
