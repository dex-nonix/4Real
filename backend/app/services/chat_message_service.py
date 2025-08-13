from __future__ import annotations

from .crud_service import CrudService
from ..models.chat_message import ChatMessage


class ChatMessageService(CrudService):
    model = ChatMessage
    config = {
        'filters': {
            'fields': ['session_id', 'role'],
        },
        'sorting': {
            'default_sort': 'created_at',
            'allowed_fields': ['created_at', 'id'],
        },
        'validation': {
            'required_fields': ['session_id', 'role'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['role'],
            'display_format': 'role',
            'search_fields': [],
            'order_by': 'created_at',
        },
    }


