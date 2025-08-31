from typing import Dict, Any

from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig
from nonix_web_db.crud.crud_operations import CRUDOperations

from .agentic_tools import AgenticTools


class AgenticCrudTools(AgenticTools):
    """Generic CRUD-enabled tool base.

    Subclasses define as class attributes:
      - prefix: str (e.g., "album", "track")
      - config: CRUDConfig (contains model, create_schema, update_schema, etc.)
    """

    prefix: str = None
    config: CRUDConfig = None

    def __init__(self):
        super().__init__()
        if self.config is None:
            raise ValueError("AgenticCrudTools subclass must define 'config' as class attribute")
        self._crud = CRUDOperations(self.config.model, self.config)

    async def create(self, **kwargs) -> Dict[str, Any]:
        """Create a new item"""
        async with AsyncSessionLocal() as session:
            create_data = self.config.create_schema(**kwargs)
            result = await self._crud.create(create_data, session)
            return {"success": True, "data": result.to_dict()}

    async def update(self, item_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing item"""
        async with AsyncSessionLocal() as session:
            update_data = self.config.update_schema(**kwargs)
            result = await self._crud.update(item_id, update_data, session)
            return {"success": True, "data": result.to_dict()}

    async def delete(self, item_id: int) -> Dict[str, Any]:
        """Delete an item"""
        async with AsyncSessionLocal() as session:
            await self._crud.delete(item_id, session)
            return {"success": True}

    async def get(self, item_id: int) -> Dict[str, Any]:
        """Get details of a single item"""
        async with AsyncSessionLocal() as session:
            item = await self._crud.get_one(item_id, session)
            return {"success": True, "data": item.to_dict()}

    async def list(self, **query_params) -> Dict[str, Any]:
        """List items"""
        async with AsyncSessionLocal() as session:
            result = await self._crud.get_all(query_params or {}, session)
            return {"success": True, "data": result.get("data", []), "pagination": result.get("pagination")}


