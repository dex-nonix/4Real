from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from nonix_web_agentic.schemas.persona_mcp_server_schemas import PersonaMCPServerCreate, PersonaMCPServerUpdate, PersonaMCPServerInDbModel
from ..models.persona_mcp_server import PersonaMCPServer


class PersonaMCPServerService(BaseCrudService):
    config = CRUDConfig(
        model=PersonaMCPServer,
        create_schema=PersonaMCPServerCreate,
        update_schema=PersonaMCPServerUpdate,
        response_schema=PersonaMCPServerInDbModel,
        filters=FilterConfig(
            allowed_fields=['persona_id', 'mcp_server_id', 'is_active']
        ),
        sorting=SortingConfig(
            default_sort='id',
            allowed_fields=['id', 'persona_id', 'mcp_server_id', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['persona_id', 'mcp_server_id'],
            display_format='{id}',
            search_fields=[]
        )
    )
