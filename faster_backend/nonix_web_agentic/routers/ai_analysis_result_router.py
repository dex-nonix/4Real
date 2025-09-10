from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.di import Inject
from nonix_web_agentic.services.ai_analysis_result_service import AIAnalysisResultService


@router("/ai-analysis-results", tags=["AI Analysis Results"])
class AIAnalysisResultRouter(NxWebServerCrudRouter):
    service: AIAnalysisResultService = Inject(AIAnalysisResultService)
