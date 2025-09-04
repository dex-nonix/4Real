from nonix_web.router.web_server_router import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .chat_history_schemas import ChatHistoryCreate, ChatHistoryUpdate, ChatHistoryInDbModel
from ...models.chat_history import ChatHistory


@routed_service("/chat-histories", tags=["Chat Histories"])
class ChatHistoryRouter(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=ChatHistory,
        create_schema=ChatHistoryCreate,
        update_schema=ChatHistoryUpdate,
        response_schema=ChatHistoryInDbModel,
        filters=FilterConfig(
            allowed_fields=['session_id', 'title']
        ),
        sorting=SortingConfig(
            default_sort='updated_at',
            allowed_fields=['created_at', 'updated_at', 'title', 'message_count']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['title', 'summary'],
            display_format='{title}',
            search_fields=['title'],
            order_by='updated_at'
        )
    )
