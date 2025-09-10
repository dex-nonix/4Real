from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from ..services.chat_prompt_service import ChatPromptService


@router("/chat-prompts", tags=["Chat Prompts"])
class ChatPromptRouter(NxWebServerCrudRouter):
    service: ChatPromptService = NxInject(ChatPromptService)
