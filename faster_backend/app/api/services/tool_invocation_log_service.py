from __future__ import annotations

from .crud_service import CrudService
from ...models.tool_invocation_log import ToolInvocationLog


class ToolInvocationLogService(CrudService):
    model = ToolInvocationLog
    config = {
        'filters': {
            'fields': ['session_id', 'message_id', 'tool_name', 'status'],
        },
        'sorting': {
            'default_sort': 'started_at',
            'allowed_fields': ['started_at', 'completed_at', 'duration_ms'],
        },
        'validation': {
            'required_fields': ['session_id', 'tool_name', 'status'],
            'unique_fields': [],
        },
        'selector': {
            'fields': ['tool_name', 'status'],
            'display_format': 'tool_name',
            'search_fields': ['tool_name'],
            'order_by': 'started_at',
        },
    }
