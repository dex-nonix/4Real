from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.ai_model_mapping_service import AIModelMappingService


@router("/ai-model-mappings", tags=["AI Model Mappings"])
class AIModelMappingRouter(NxWebServerCrudRouter):
    service: AIModelMappingService = Inject(AIModelMappingService)
