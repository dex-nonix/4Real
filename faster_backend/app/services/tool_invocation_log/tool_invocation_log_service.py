from .tool_invocation_log_schemas import ToolInvocationLogCreate, ToolInvocationLogUpdate, ToolInvocationLogInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import ToolInvocationLog


@routed_service("/tool_invocation_logs", tags=["Tool Invocation Logs"])
class ToolInvocationLogService(GenericCRUDService):
    config = CRUDConfig(
        model=ToolInvocationLog,
        create_schema=ToolInvocationLogCreate,
        update_schema=ToolInvocationLogUpdate,
        response_schema=ToolInvocationLogInDB,
        filters=FilterConfig(
            allowed_fields=['session_id', 'message_id', 'tool_name', 'status']
        ),
        sorting=SortingConfig(
            default_sort='started_at',
            allowed_fields=['started_at', 'completed_at', 'duration_ms']
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
