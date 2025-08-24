from .ai_model_mapping_schemas import AIModelMappingCreate, AIModelMappingUpdate, AIModelMappingInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import AIModelMapping


@routed_service("/ai_model_mappings", tags=["AI Model Mappings"])
class AIModelMappingService(GenericCRUDService):
    config = CRUDConfig(
        model=AIModelMapping,
        create_schema=AIModelMappingCreate,
        update_schema=AIModelMappingUpdate,
        response_schema=AIModelMappingInDB,
        filters=FilterConfig(
            allowed_fields=['provider_id', 'name', 'model_name', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'model_name', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['name', 'model_name'],
            display_format='{name}',
            search_fields=['name', 'model_name']
        )
    )
