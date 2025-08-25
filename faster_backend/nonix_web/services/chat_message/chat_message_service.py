from .chat_message_schemas import ChatMessageCreate, ChatMessageUpdate, ChatMessageInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import ChatMessage


@routed_service("/chat-messages", tags=["Chat Messages"])
class ChatMessageService(GenericCRUDService):
    config = CRUDConfig(
        model=ChatMessage,
        create_schema=ChatMessageCreate,
        update_schema=ChatMessageUpdate,
        response_schema=ChatMessageInDB,
        filters=FilterConfig(
            allowed_fields=['history_id', 'role', 'message_type']
        ),
        sorting=SortingConfig(
            default_sort='created_at',
            allowed_fields=['created_at', 'id', 'role']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['role', 'message_type'],
            display_format='{role}',
            search_fields=['role'],
            order_by='created_at'
        )
    )
