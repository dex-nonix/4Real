from .ai_analysis_result_schemas import AIAnalysisResultCreate, AIAnalysisResultUpdate, AIAnalysisResultInDB
from ..base_service import routed_service
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import AIAnalysisResult


@routed_service("/ai_analysis_results", tags=["AI Analysis Results"])
class AIAnalysisResultService(GenericCRUDService):
    config = CRUDConfig(
        model=AIAnalysisResult,
        create_schema=AIAnalysisResultCreate,
        update_schema=AIAnalysisResultUpdate,
        response_schema=AIAnalysisResultInDB,
        filters=FilterConfig(
            allowed_fields=['track_id', 'provider_id', 'analysis_type']
        ),
        sorting=SortingConfig(
            default_sort='id',
            allowed_fields=['id', 'analysis_type', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['analysis_type'],
            display_format='{analysis_type}',
            search_fields=['analysis_type']
        )
    )
