from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.chat_history_service import ChatHistoryService


@router("/chat-histories", tags=["Chat Histories"])
class ChatHistoryRouter(NxWebServerCrudRouter):
    service: ChatHistoryService = Inject(ChatHistoryService)
