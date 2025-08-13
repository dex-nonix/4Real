from __future__ import annotations

from .crud_service import CrudService
from ..models.chat_session import ChatSession


class ChatSessionService(CrudService):
    model = ChatSession
    config = {
        'filters': {
            'fields': ['persona_id', 'title', 'created_by'],
        },
        'sorting': {
            'default_sort': 'created_at',
            'allowed_fields': ['created_at', 'updated_at', 'title'],
        },
        'validation': {
            'required_fields': ['persona_id', 'title'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['title'],
            'display_format': 'title',
            'search_fields': ['title', 'created_by'],
            'order_by': 'created_at',
        },
    }


