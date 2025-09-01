from typing import Optional, List, Generic, TypeVar, Any, Type, Dict

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class PaginationInfo(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: PaginationInfo


class BulkOperationsPayload(BaseModel):
    operation: str = Field(..., pattern="^(delete|update)$")
    ids: List[int]
    data: Optional[Dict[str, Any]] = None


class SelectorItem(BaseModel):
    id: int
    value: int
    label: str


# --- Pydantic Models for the Configuration ---
class OperationsConfig(BaseModel):
    create: bool = True
    read: bool = True
    update: bool = True
    delete: bool = True
    list: bool = True
    search: bool = True
    bulk: bool = True
    selector: bool = True


class FilterConfig(BaseModel):
    allowed_fields: List[str] = Field(default_factory=list, description="Fields that can be filtered on (empty = all fields allowed)")
    auto_filters: Dict[str, str] = Field(default_factory=dict, description="field_name: context_key for automatic filtering")
    default_filters: Dict[str, Any] = Field(default_factory=dict, description="field_name: default_value for automatic filtering")
    search_fields: List[str] = Field(default_factory=list, description="Fields to search by default")
    context_aware: bool = True  # enable auto-filtering by context
    strict_filtering: bool = False  # if True, only allowed_fields can be filtered; if False, all fields allowed


class SortingConfig(BaseModel):
    default_sort: str = 'id'
    allowed_fields: List[str] = []


class ValidationConfig(BaseModel):
    unique_fields: List[str] = []


class PaginationConfig(BaseModel):
    default_page_size: int = 20
    max_page_size: int = 100


class SelectorConfig(BaseModel):
    fields: List[str] = ['name']
    display_format: Optional[str] = None
    search_fields: List[str] = ['name']
    limit: int = 100
    order_by: str = 'name'


class CRUDConfig(BaseModel):
    """The single source of truth for a CRUD service's configuration."""
    model: Type
    create_schema: Type[BaseModel]
    update_schema: Type[BaseModel]
    response_schema: Type[BaseModel]
    operations: OperationsConfig = Field(default_factory=OperationsConfig)
    filters: FilterConfig = Field(default_factory=FilterConfig)
    sorting: SortingConfig = Field(default_factory=SortingConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)
    selector: SelectorConfig = Field(default_factory=SelectorConfig)

    model_config = ConfigDict(arbitrary_types_allowed=True)
