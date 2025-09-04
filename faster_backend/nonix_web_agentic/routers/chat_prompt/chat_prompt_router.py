from nonix_web.router.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .chat_prompt_schemas import ChatPromptCreate, ChatPromptUpdate, ChatPromptInDbModel
from ...models.chat_prompt import ChatPrompt


@routed_service("/chat-prompts", tags=["Chat Prompts"])
class ChatPromptRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=ChatPrompt,
        create_schema=ChatPromptCreate,
        update_schema=ChatPromptUpdate,
        response_schema=ChatPromptInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'description', 'template_id']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at', 'updated_at', 'template_id']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name', 'description']
        )
    )
