from typing import Optional, Dict, Any, Type

from pydantic import BaseModel

from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig
from nonix_web_db.crud.crud_operations import CRUDOperations

from .agentic_tools import AgenticTools, tool


class AgenticCrudTools(AgenticTools):
    """Generic CRUD-enabled tool base.

    Subclasses set:
      - self.model
      - self.crud_config
    and inherit generic CRUD tool methods which can be overridden.
    """

    def __init__(self, model: Type, crud_config: CRUDConfig):
        super().__init__()
        self.model = model
        self.crud_config = crud_config
        self._crud = CRUDOperations(self.model, self.crud_config)

    def _get_owner_filter(self, owner_id: int, owner_field: str = 'artist_id') -> Dict[str, Any]:
        return {f"filter_{owner_field}": str(owner_id)}

    @tool("crud:create")
    async def create(self, data: BaseModel) -> Any:
        async with AsyncSessionLocal() as session:
            return await self._crud.create(data, session)

    @tool("crud:update")
    async def update(self, item_id: int, data: BaseModel) -> Any:
        async with AsyncSessionLocal() as session:
            return await self._crud.update(item_id, data, session)

    @tool("crud:delete")
    async def delete(self, item_id: int) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            await self._crud.delete(item_id, session)
            return {"success": True}

    @tool("crud:get")
    async def get(self, item_id: int) -> Any:
        async with AsyncSessionLocal() as session:
            return await self._crud.get_one(item_id, session)

    @tool("crud:list")
    async def list(self, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            return await self._crud.get_all(query_params or {}, session)


