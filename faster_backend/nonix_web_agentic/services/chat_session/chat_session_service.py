from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from nonix_web.services.base_service import routed_service
from .chat_session_schemas import ChatSessionCreate, ChatSessionUpdate, ChatSessionInDbModel
from ...models.chat_session import ChatSession


@routed_service("/chat-sessions", tags=["Chat Sessions"])
class ChatSessionService(GenericCRUDService):
    config = CRUDConfig(
        model=ChatSession,
        create_schema=ChatSessionCreate,
        update_schema=ChatSessionUpdate,
        response_schema=ChatSessionInDbModel,
        filters=FilterConfig(
            allowed_fields=['persona_id', 'session_name', 'session_icon', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='created_at',
            allowed_fields=['created_at', 'updated_at', 'session_name']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['session_name', 'session_icon'],
            display_format='{session_name}',
            search_fields=['session_name'],
            order_by='created_at'
        )
    )
