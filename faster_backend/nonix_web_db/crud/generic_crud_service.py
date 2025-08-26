from typing import Dict, Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, or_
from starlette import status
from starlette.requests import Request

from nonix_web.services.base_service import BaseService
from .models_and_schemas import BulkOperationsPayload, PaginatedResponse, SelectorItem, CRUDConfig
from .models_and_schemas import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig
from .query_processor import QueryProcessor
from .types import ModelType
from .utils import get_list_for_query_params, get_item_by_id, create_paginated_response, execute_query_all

__all__ = [
    "CRUDConfig",
    "FilterConfig",
    "SortingConfig",
    "ValidationConfig",
    "SelectorConfig",
    "GenericCRUDService",
]

from ..plugin import AsyncSessionLocal


class GenericCRUDService(BaseService):
    config: CRUDConfig

    def __init__(self, app, router: APIRouter):
        super().__init__(app, router)
        self.model = self.config.model
        self.query_processor = QueryProcessor(model=self.model, config=self.config)
        self._register_routes()

    async def create(self, data: BaseModel) -> ModelType:
        async with AsyncSessionLocal() as session:
            instance = self.model(**data.model_dump())
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def get_all(self, query_params: dict) -> Dict:
        async with AsyncSessionLocal() as session:
            return await get_list_for_query_params(session, self.model, query_params)

    async def get_one(self, item_id: int) -> Optional[ModelType]:
        async with AsyncSessionLocal() as session:
            return await get_item_by_id(session, self.model, item_id)

    async def update(self, item_id: int, data: BaseModel) -> ModelType:
        async with AsyncSessionLocal() as session:
            instance = await get_item_by_id(session, self.model, item_id)
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def delete(self, item_id: int):
        async with AsyncSessionLocal() as session:
            instance = await get_item_by_id(session, self.model, item_id)
            await session.delete(instance)
            await session.commit()

    async def search(self, request: Request, query_params: dict) -> Dict:
        async with AsyncSessionLocal() as session:
            q = request.query_params.get("q", "")
            if not q:
                return create_paginated_response(data=[], page=1, per_page=10, total=0)
            model = self.model
            fields_param = request.query_params.get("fields", "")
            search_fields = (
                fields_param.split(",") if
                fields_param else
                [c.name for c in model.__table__.columns if hasattr(c.type, "length")]
            )
            conditions = [
                getattr(model, field).ilike(f"%{q}%")
                for field in search_fields
                if hasattr(model, field)
            ]
            query_params["filters"].extend(conditions)

            return await get_list_for_query_params(session, model, query_params)

    def _format_selector_label(self, item: ModelType) -> str:
        selector_cfg = self.config.selector
        if selector_cfg.display_format:
            try:
                item_dict = {c.name: getattr(item, c.name) for c in item.__table__.columns}
                return selector_cfg.display_format.format(**item_dict)
            except (KeyError, AttributeError):
                return str(item.id)
        if selector_cfg.fields:
            return str(getattr(item, selector_cfg.fields[0], item.id))
        return str(item.id)

    async def selector(self, q: Optional[str]) -> List[Dict]:
        async with AsyncSessionLocal() as session:
            selector_cfg = self.config.selector
            query = select(self.model)
            if q and selector_cfg.search_fields:
                conditions = [getattr(self.model, field).ilike(f"%{q}%") for field in selector_cfg.search_fields]
                query = query.where(or_(*conditions))
            query = query.order_by(
                getattr(self.model, selector_cfg.order_by).asc()
            ).limit(selector_cfg.limit)
            items = await execute_query_all(session, query)
            return [
                {
                    "id": item.id,
                    "value": item.id,
                    "label": self._format_selector_label(item),
                }
                for item in items
            ]

    async def bulk(self, payload: BulkOperationsPayload):
        async with AsyncSessionLocal() as session:
            query = select(self.model).where(self.model.id.in_(payload.ids))
            items = await execute_query_all(session, query)
            if payload.operation == "delete":
                for item in items:
                    await session.delete(item)
                msg = f"Deleted {len(items)} records successfully"
            elif payload.operation == "update":
                for item in items:
                    for key, value in payload.data.items():
                        setattr(item, key, value)
                msg = f"Updated {len(items)} records successfully"
            await session.commit()
            return {"message": msg}

    def _register_routes(self) -> None:
        async def _validate(data: BaseModel, item_id: Optional[int] = None):
            if not self.config.validation.unique_fields:
                return
            async with AsyncSessionLocal() as session:
                for field in self.config.validation.unique_fields:
                    value = getattr(data, field, None)
                    if value is not None:
                        q = select(self.model).where(getattr(self.model, field) == value)
                        if item_id:
                            q = q.where(self.model.id != item_id)
                        if (await session.execute(q)).scalar_one_or_none():
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail=f"Item with this '{field}' already exists.",
                            )

        ops = self.config.operations
        if ops.create:
            @self.router.post(
                "/",
                response_model=self.config.response_schema,
                status_code=status.HTTP_201_CREATED,
            )
            async def create(data: self.config.create_schema):
                await _validate(data)
                return await self.create(data)

        if ops.list:
            @self.router.get(
                "/", response_model=PaginatedResponse[self.config.response_schema]
            )
            async def list_all(request: Request):
                q_params = await self.query_processor(request)
                return await self.get_all(q_params)

        if ops.read:
            @self.router.get("/{item_id}", response_model=self.config.response_schema)
            async def read_one(item_id: int):
                return await self.get_one(item_id)

        if ops.update:
            @self.router.put("/{item_id}", response_model=self.config.response_schema)
            async def update(item_id: int, data: self.config.update_schema):
                await _validate(data, item_id)
                return await self.update(item_id, data)

        if ops.delete:
            @self.router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
            async def delete(item_id: int):
                await self.delete(item_id)

        if ops.search:
            @self.router.get(
                "/search/",
                response_model=PaginatedResponse[self.config.response_schema],
            )
            async def search(request: Request):
                q_params = await self.query_processor(request)
                return await self.search(request, q_params)

        if ops.bulk:
            @self.router.post("/bulk/", response_model=Dict[str, str])
            async def bulk(payload: BulkOperationsPayload):
                return await self.bulk(payload)

        if ops.selector:
            @self.router.get("/selector/", response_model=List[SelectorItem])
            async def selector(q: Optional[str] = None):
                return await self.selector(q)

            @self.router.get("/selector/{item_id}", response_model=SelectorItem)
            async def single_selector(item_id: int):
                item = await self.get_one(item_id)
                return {
                    "id": item.id,
                    "value": item.id,
                    "label": self._format_selector_label(item),
                }
