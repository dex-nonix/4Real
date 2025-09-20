from typing import Dict, Optional, List

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from nonix_web.router.web_server_router import NxWebServerRouter
from .base_crud_service import BaseCrudService
from .models_and_schemas import BulkOperationsPayload, PaginatedResponse, SelectorItem, CRUDConfig
from .models_and_schemas import FilterConfig, SortingConfig, ValidationConfig, SelectorConfig
from .query_processor import QueryProcessor

__all__ = [
    "CRUDConfig",
    "FilterConfig",
    "SortingConfig",
    "ValidationConfig",
    "SelectorConfig",
    "NxWebServerCrudRouter",
]


class NxWebServerCrudRouter(NxWebServerRouter):
    service: BaseCrudService  # Inject service instead of having config
    query_processor:QueryProcessor

    def __init__(self):
        super().__init__()
        self.query_processor = QueryProcessor(self.service.config)

    def register_routes(self, router):
        super().register_routes(router)
        self._register_routes(router)

    # All CRUD operations now delegate to the injected service
    def _register_routes(self, router) -> None:
        # Use cached service reference (injection already triggered in _init_components)
        service = self.service
        config = service.config
        ops = config.operations

        if ops.create:
            @router.post(
                "/",
                response_model=config.response_schema,
                status_code=status.HTTP_201_CREATED,
            )
            async def create(data: config.create_schema):
                return await service.create(data)

        if ops.list:
            @router.get("/", response_model=PaginatedResponse[config.response_schema])
            async def list_all(request: Request):
                q_params = await self.query_processor(request)
                return await service.get_all(q_params)

        if ops.search:
            @router.get("/search", response_model=PaginatedResponse[config.response_schema])
            async def search(request: Request):
                q_params = await self.query_processor(request)
                q = request.query_params.get("q", "")
                # Pass through optional fields param for parity with previous behavior
                fields_param = request.query_params.get("fields")
                if fields_param is not None:
                    q_params = dict(q_params)
                    q_params["fields"] = fields_param
                return await service.search(q_params, q)

        if ops.bulk:
            @router.post("/bulk", response_model=Dict[str, str])
            async def bulk(payload: BulkOperationsPayload):
                return await service.bulk_update(payload.ids, payload.data)

        if ops.selector:
            @router.get("/selector", response_model=List[SelectorItem])
            async def selector(q: Optional[str] = None):
                return await service.selector(q)

            @router.get("/selector/{item_id}", response_model=SelectorItem)
            async def single_selector(item_id: int):
                return await service.single_selector(item_id)

        if ops.delete:
            @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
            async def delete(item_id: int):
                await service.delete(item_id)

        if ops.read:
            @router.get("/{item_id}", response_model=config.response_schema)
            async def read_one(item_id: int):
                return await service.get_one(item_id)

        if ops.update:
            @router.put("/{item_id}", response_model=config.response_schema)
            async def update(item_id: int, data: config.update_schema):
                return await service.update(item_id, data)
