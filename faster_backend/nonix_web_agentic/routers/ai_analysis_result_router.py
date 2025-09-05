from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.ai_analysis_result_service import AIAnalysisResultService


@router("/ai-analysis-results", tags=["AI Analysis Results"])
class AIAnalysisResultRouter(NxWebServerCrudRouter):
    service: AIAnalysisResultService = Inject(AIAnalysisResultService)
