from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_agentic.services.chat_history_service import ChatHistoryService


@router("/chat-histories", tags=["Chat Histories"])
class ChatHistoryRouter(NxWebServerCrudRouter):
    service: ChatHistoryService = Inject(ChatHistoryService)
