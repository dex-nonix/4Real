from .crud_service import CrudService
from ...models.ai_analysis_result import AIAnalysisResult


class AIAnalysisResultService(CrudService):
    model = AIAnalysisResult
    config = {
        'filters': {
            'fields': ['track_id', 'provider_id', 'analysis_type'],
        },
        'sorting': {
            'default_sort': 'id',
            'allowed_fields': ['id', 'analysis_type', 'created_at'],
        },
        'validation': {
            'required_fields': ['track_id', 'provider_id', 'analysis_type'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['analysis_type'],
            'display_format': 'analysis_type',
            'search_fields': ['analysis_type'],
        },
    }
