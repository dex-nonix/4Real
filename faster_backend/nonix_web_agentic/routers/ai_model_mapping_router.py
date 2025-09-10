from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.di import Inject
from nonix_web_agentic.services.ai_model_mapping_service import AIModelMappingService


@router("/ai-model-mappings", tags=["AI Model Mappings"])
class AIModelMappingRouter(NxWebServerCrudRouter):
    service: AIModelMappingService = Inject(AIModelMappingService)
