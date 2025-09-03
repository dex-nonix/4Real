from nonix_web.services.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .ai_analysis_result_schemas import AIAnalysisResultCreate, AIAnalysisResultUpdate, AIAnalysisResultInDbModel
from ...models.ai_analysis_result import AIAnalysisResult


@routed_service("/ai-analysis-results", tags=["AI Analysis Results"])
class AIAnalysisResultService(GenericCRUDService):
    config = CRUDConfig(
        model=AIAnalysisResult,
        create_schema=AIAnalysisResultCreate,
        update_schema=AIAnalysisResultUpdate,
        response_schema=AIAnalysisResultInDbModel,
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
