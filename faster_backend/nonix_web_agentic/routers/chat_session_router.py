from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.di import Inject
from nonix_web_agentic.services.chat_session_service import ChatSessionService


@router("/chat-sessions", tags=["Chat Sessions"])
class ChatSessionRouter(NxWebServerCrudRouter):
    service: ChatSessionService = Inject(ChatSessionService)
