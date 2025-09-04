from typing import Dict, Optional, List

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select
from starlette import status
from starlette.requests import Request

from nonix_web.router.web_server_router import NxWebServerRouter
from .models_and_schemas import BulkOperationsPayload, PaginatedResponse, SelectorItem, CRUDConfig
from .models_and_schemas import FilterConfig, SortingConfig, ValidationConfig, SelectorConfig
from .query_processor import QueryProcessor
from .types import ModelType
from .utils import execute_query_all
from .crud_operations import CRUDOperations

__all__ = [
    "CRUDConfig",
    "FilterConfig",
    "SortingConfig",
    "ValidationConfig",
    "SelectorConfig",
    "NxWebServerCrudRouter",
]

from ..plugin import AsyncSessionLocal


class NxWebServerCrudRouter(NxWebServerRouter):
    config: CRUDConfig

    def __init__(self, router: APIRouter):
        super().__init__(router)
        self.model = self.config.model
        self.query_processor = QueryProcessor(model=self.model, config=self.config)
        self.crud_operations = CRUDOperations(self.model, self.config)
        self._register_routes()

    async def create(self, data: BaseModel) -> ModelType:
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.create(data, session)

    async def get_all(self, query_params: dict) -> Dict:
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.get_all(query_params, session)

    async def get_one(self, item_id: int) -> Optional[ModelType]:
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.get_one(item_id, session)

    async def update(self, item_id: int, data: BaseModel) -> ModelType:
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.update(item_id, data, session)

    async def delete(self, item_id: int):
        async with AsyncSessionLocal() as session:
            await self.crud_operations.delete(item_id, session)

    async def search(self, request: Request, query_params: dict) -> Dict:
        async with AsyncSessionLocal() as session:
            q = request.query_params.get("q", "")
            # Pass through optional fields param for parity with previous behavior
            fields_param = request.query_params.get("fields")
            if fields_param is not None:
                query_params = dict(query_params)
                query_params["fields"] = fields_param
            return await self.crud_operations.search(query_params, q, session)

    def _format_selector_label(self, item: ModelType) -> str:
        return self.crud_operations._format_selector_label(item)

    async def selector(self, q: Optional[str]) -> List[Dict]:
        async with AsyncSessionLocal() as session:
            return await self.crud_operations.selector(q, session)

    async def bulk(self, payload: BulkOperationsPayload):
        async with AsyncSessionLocal() as session:
            if payload.operation == "delete":
                # Match previous behavior: operate on found items in a single transaction
                query = select(self.model).where(self.model.id.in_(payload.ids))
                items = await execute_query_all(session, query)
                for item in items:
                    await session.delete(item)
                await session.commit()
                msg = f"Deleted {len(items)} records successfully"
            elif payload.operation == "update":
                await self.crud_operations.bulk_update(payload.ids, payload.data, session)
                msg = f"Updated {len(payload.ids)} records successfully"
            return {"message": msg}

    def _register_routes(self) -> None:

        ops = self.config.operations
        if ops.create:
            @self.router.post(
                "/",
                response_model=self.config.response_schema,
                status_code=status.HTTP_201_CREATED,
            )
            async def create(data: self.config.create_schema):
                return await self.create(data)

        if ops.list:
            @self.router.get("/", response_model=PaginatedResponse[self.config.response_schema])
            async def list_all(request: Request):
                q_params = await self.query_processor(request)
                return await self.get_all(q_params)

        if ops.search:
            @self.router.get("/search", response_model=PaginatedResponse[self.config.response_schema] )
            async def search(request: Request):
                q_params = await self.query_processor(request)
                return await self.search(request, q_params)

        if ops.bulk:
            @self.router.post("/bulk", response_model=Dict[str, str])
            async def bulk(payload: BulkOperationsPayload):
                return await self.bulk(payload)

        if ops.selector:
            @self.router.get("/selector", response_model=List[SelectorItem])
            async def selector(q: Optional[str] = None):
                return await self.selector(q)

            @self.router.get("/selector/{item_id}", response_model=SelectorItem)
            async def single_selector(item_id: int):
                async with AsyncSessionLocal() as session:
                    return await self.crud_operations.single_selector(item_id, session)

        if ops.delete:
            @self.router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
            async def delete(item_id: int):
                await self.delete(item_id)

        if ops.read:
            @self.router.get("/{item_id}", response_model=self.config.response_schema)
            async def read_one(item_id: int):
                return await self.get_one(item_id)

        if ops.update:
            @self.router.put("/{item_id}", response_model=self.config.response_schema)
            async def update(item_id: int, data: self.config.update_schema):
                return await self.update(item_id, data)
