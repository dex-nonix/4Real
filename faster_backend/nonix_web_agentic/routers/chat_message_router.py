from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from ...services.chat_message_service import ChatMessageService


@router("/chat-messages", tags=["Chat Messages"])
class ChatMessageRouter(NxWebServerCrudRouter):
    service: ChatMessageService = Inject(ChatMessageService)
