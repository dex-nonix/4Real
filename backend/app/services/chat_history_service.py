from __future__ import annotations

from .crud_service import CrudService
from ..models.chat_history import ChatHistory


class ChatHistoryService(CrudService):
    model = ChatHistory
    config = {
        'filters': {
            'fields': ['session_id', 'title'],
        },
        'sorting': {
            'default_sort': 'updated_at',
            'allowed_fields': ['created_at', 'updated_at', 'title', 'message_count'],
        },
        'validation': {
            'required_fields': ['session_id', 'title'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['title', 'summary'],
            'display_format': 'title',
            'search_fields': ['title'],
            'order_by': 'updated_at',
        },
    }
