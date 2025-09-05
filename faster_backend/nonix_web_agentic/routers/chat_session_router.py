from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.chat_session_service import ChatSessionService


@router("/chat-sessions", tags=["Chat Sessions"])
class ChatSessionRouter(NxWebServerCrudRouter):
    service: ChatSessionService = Inject(ChatSessionService)
