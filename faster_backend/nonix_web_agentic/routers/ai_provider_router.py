from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_agentic.services.ai_provider_service import AIProviderService


@router("/ai-providers", tags=["AI Providers"])
class AIProviderRouter(NxWebServerCrudRouter):
    service: AIProviderService = Inject(AIProviderService)
