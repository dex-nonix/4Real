from .crud_service import CrudService
from ...models.chat_message import ChatMessage


class ChatMessageService(CrudService):
    model = ChatMessage
    config = {
        'filters': {
            'fields': ['history_id', 'role', 'message_type'],
        },
        'sorting': {
            'default_sort': 'created_at',
            'allowed_fields': ['created_at', 'id', 'role'],
        },
        'validation': {
            'required_fields': ['history_id', 'role', 'message_type'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['role', 'message_type'],
            'display_format': 'role',
            'search_fields': ['role'],
            'order_by': 'created_at',
        },
    }
