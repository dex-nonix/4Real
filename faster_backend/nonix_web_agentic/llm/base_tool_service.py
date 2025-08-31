from typing import Dict, Any, List, Tuple, Callable, Type, Optional, TYPE_CHECKING
from abc import ABC

from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig
from nonix_web_db.crud.crud_operations import CRUDOperations
from pydantic import BaseModel

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


# Decorator to mark methods as tools
def tool(name: str):
    def decorator(func):
        func._tool_name = name
        return func
    return decorator


class BaseToolService(ABC):
    """Base class for creating DRY CRUD tool services.

    Subclasses should:
    1. Set self.model and self.crud_config in __init__
    2. Decorate methods with @tool("tool:name") to expose them
    3. Override CRUD methods if custom logic is needed
    """

    def __init__(self):
        self.model: Type['DeclarativeBase'] = None
        self.crud_config: CRUDConfig = None
        self._crud_operations: CRUDOperations = None

    @property
    def crud_operations(self) -> CRUDOperations:
        if self._crud_operations is None and self.model and self.crud_config:
            self._crud_operations = CRUDOperations(self.model, self.crud_config)
        return self._crud_operations

    async def create(self, data: BaseModel) -> Dict[str, Any]:
        """Generic create operation using CRUDOperations."""
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.create(data, session)

    async def update(self, item_id: int, data: BaseModel) -> Dict[str, Any]:
        """Generic update operation using CRUDOperations."""
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.update(item_id, data, session)

    async def delete(self, item_id: int) -> Dict[str, Any]:
        """Generic delete operation using CRUDOperations."""
        async with AsyncSessionLocal() as session:
            await self.crud_operations.delete(item_id, session)
            return {"success": True, "message": f"{self.model.__name__} deleted successfully"}

    async def get_one(self, item_id: int) -> Dict[str, Any]:
        """Generic get_one operation using CRUDOperations."""
        async with AsyncSessionLocal() as session:
            item = await self.crud_operations.get_one(item_id, session)
            return item.to_dict()

    async def list(self, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic list operation using CRUDOperations."""
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.get_all(query_params or {}, session)

    def to_agentic_tools(self) -> List[Tuple[str, Callable[..., Any]]]:
        """Extract all @tool decorated methods and return them as (name, func) tuples."""
        tools = []
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue

            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_tool_name'):
                tool_name = getattr(attr, '_tool_name')
                tools.append((tool_name, attr))

        return tools

    def _verify_ownership(self, item_id: int, owner_field: str = 'artist_id') -> bool:
        """Helper method to verify ownership of an item."""
        # This is a placeholder - subclasses can implement custom ownership verification
        return True

    def _get_owner_filter(self, owner_id: int, owner_field: str = 'artist_id') -> Dict[str, Any]:
        """Helper method to create ownership filter."""
        return {f"filter_{owner_field}": str(owner_id)}


# CRUD Tool Service for standard CRUD operations
class CRUDToolService(BaseToolService):
    """Generic CRUD tool service that provides standard create/update/delete/list operations."""

    def __init__(self, model: Type['DeclarativeBase'], crud_config: CRUDConfig):
        super().__init__()
        self.model = model
        self.crud_config = crud_config

    @tool("create")
    async def create_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item."""
        # Convert dict to Pydantic model
        create_schema = self.crud_config.create_schema
        if create_schema:
            create_data = create_schema(**data)
            result = await self.create(create_data)
            return {"success": True, "item": result.to_dict()}
        return {"success": False, "error": "No create schema defined"}

    @tool("update")
    async def update_item(self, item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing item."""
        # Convert dict to Pydantic model
        update_schema = self.crud_config.update_schema
        if update_schema:
            update_data = update_schema(**data)
            result = await self.update(item_id, update_data)
            return {"success": True, "item": result.to_dict()}
        return {"success": False, "error": "No update schema defined"}

    @tool("delete")
    async def delete_item(self, item_id: int) -> Dict[str, Any]:
        """Delete an item."""
        return await self.delete(item_id)

    @tool("get")
    async def get_item(self, item_id: int) -> Dict[str, Any]:
        """Get a single item."""
        return await self.get_one(item_id)

    @tool("list")
    async def list_items(self, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List items with optional filtering."""
        return await self.list(query_params or {})
