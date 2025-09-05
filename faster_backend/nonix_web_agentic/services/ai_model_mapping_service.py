from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.ai_model_mapping.ai_model_mapping_schemas import AIModelMappingCreate, AIModelMappingUpdate, AIModelMappingInDbModel
from ..models.ai_model_mapping import AIModelMapping


class AIModelMappingService(BaseCrudService):
    config = CRUDConfig(
        model=AIModelMapping,
        create_schema=AIModelMappingCreate,
        update_schema=AIModelMappingUpdate,
        response_schema=AIModelMappingInDbModel,
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
