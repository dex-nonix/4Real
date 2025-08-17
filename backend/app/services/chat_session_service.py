from __future__ import annotations

from .crud_service import CrudService
from ..models.chat_session import ChatSession


class ChatSessionService(CrudService):
    model = ChatSession
    config = {
        'filters': {
            'fields': ['persona_id', 'session_name', 'session_icon', 'is_active'],
        },
        'sorting': {
            'default_sort': 'created_at',
            'allowed_fields': ['created_at', 'updated_at', 'session_name'],
        },
        'validation': {
            'required_fields': ['persona_id'],  # session_name is optional
            'unique_fields': [],
        },
        'selector': {
            'fields': ['session_name', 'session_icon'],
            'display_format': 'session_name',
            'search_fields': ['session_name'],
            'order_by': 'created_at',
        },
    }


