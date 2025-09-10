from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from nonix_web_agentic.services.chat_message_service import ChatMessageService


@router("/chat-messages", tags=["Chat Messages"])
class ChatMessageRouter(NxWebServerCrudRouter):
    service: ChatMessageService = NxInject(ChatMessageService)
