from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.tool_invocation_log.tool_invocation_log_schemas import ToolInvocationLogCreate, ToolInvocationLogUpdate, ToolInvocationLogInDbModel
from ..models.tool_invocation_log import ToolInvocationLog


class ToolInvocationLogService(BaseCrudService):
    config = CRUDConfig(
        model=ToolInvocationLog,
        create_schema=ToolInvocationLogCreate,
        update_schema=ToolInvocationLogUpdate,
        response_schema=ToolInvocationLogInDbModel,
        filters=FilterConfig(
            allowed_fields=['session_id', 'message_id', 'tool_name', 'status']
        ),
        sorting=SortingConfig(
            default_sort='seq',
            allowed_fields=['seq', 'started_at', 'completed_at', 'duration_ms']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['tool_name', 'status'],
            display_format='{tool_name}',
            search_fields=['tool_name'],
            order_by='started_at'
        )
    )
