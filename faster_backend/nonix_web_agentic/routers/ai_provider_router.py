from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.ai_provider_service import AIProviderService


@router("/ai-providers", tags=["AI Providers"])
class AIProviderRouter(NxWebServerCrudRouter):
    service: AIProviderService = NxInject(AIProviderService)
