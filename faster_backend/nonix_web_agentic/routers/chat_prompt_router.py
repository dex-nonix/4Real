from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_agentic.services.chat_prompt_service import ChatPromptService


@router("/chat-prompts", tags=["Chat Prompts"])
class ChatPromptRouter(NxWebServerCrudRouter):
    service: ChatPromptService = Inject(ChatPromptService)
