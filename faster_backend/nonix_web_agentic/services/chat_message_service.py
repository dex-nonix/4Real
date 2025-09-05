from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.chat_message.chat_message_schemas import ChatMessageCreate, ChatMessageUpdate, ChatMessageInDbModel
from ..models.chat_message import ChatMessage


class ChatMessageService(BaseCrudService):
    config = CRUDConfig(
        model=ChatMessage,
        create_schema=ChatMessageCreate,
        update_schema=ChatMessageUpdate,
        response_schema=ChatMessageInDbModel,
        filters=FilterConfig(
            allowed_fields=['history_id', 'role', 'message_type']
        ),
        sorting=SortingConfig(
            default_sort='seq',
            allowed_fields=['seq', 'created_at', 'id', 'role']
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
