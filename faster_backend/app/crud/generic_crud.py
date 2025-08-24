import math
from datetime import datetime, date
from typing import Type, TypeVar, List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from pydantic import BaseModel
from sqlalchemy import select, or_, func, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from .models_and_schemas import CRUDConfig, PaginatedResponse, SelectorItem, BulkOperationsPayload
from ..database import get_db
from ..services.base_service import BaseService

ModelType = TypeVar("ModelType")


class QueryProcessor:
    def __init__(self, model: Type[ModelType], config: CRUDConfig):
        self.model = model
        self.config = config

    async def _coerce_value(self, field, raw_value: str) -> Any:
        try:
            column = getattr(self.model, field).property.columns[0]
            py_type = column.type.python_type
            if py_type is datetime: return datetime.fromisoformat(raw_value)
            if py_type is date: return date.fromisoformat(raw_value)
            return py_type(raw_value)
        except Exception:
            return raw_value

    async def __call__(self, request: Request):
        query_params = request.query_params
        filters = []
        for key, value in query_params.items():
            if key.startswith("filter_"):
                field_name = key[7:]
                if field_name not in self.config.filters.allowed_fields:
                    continue
                field = getattr(self.model, field_name)
                op, filter_value = value.split(":", 1) if ":" in value else ("eq", value)
                coerced_value = await self._coerce_value(field_name, filter_value)
                if op == "eq":
                    filters.append(field == coerced_value)
                elif op == "ne":
                    filters.append(field != coerced_value)
                elif op == "gt":
                    filters.append(field > coerced_value)
                elif op == "lt":
                    filters.append(field < coerced_value)
                elif op == "like":
                    filters.append(field.ilike(f"%{coerced_value}%"))
                elif op == "in":
                    values = [await self._coerce_value(field_name, v) for v in filter_value.split(',')]
                    filters.append(field.in_(values))
        sort_cfg = self.config.sorting
        sort_field_name = query_params.get("sort", sort_cfg.default_sort)
        order = query_params.get("order", "asc")
        sort_clause = None
        if sort_field_name in sort_cfg.allowed_fields:
            sort_field = getattr(self.model, sort_field_name)
            sort_clause = sort_field.desc() if order.lower() == "desc" else sort_field.asc()
        pag_cfg = self.config.pagination
        page = int(query_params.get("page", 1))
        per_page = min(int(query_params.get("per_page", pag_cfg.default_page_size)), pag_cfg.max_page_size)
        offset = (page - 1) * per_page
        return {"filters": filters, "sort_clause": sort_clause, "offset": offset, "limit": per_page, "page": page,
                "per_page": per_page}


class BaseCRUDService:
    def __init__(self, model: Type[ModelType], config: CRUDConfig):
        self.model = model
        self.config = config

    async def create(self, db: AsyncSession, data: BaseModel) -> ModelType:
        instance = self.model(**data.model_dump())
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def get_all(self, db: AsyncSession, query_params: dict) -> Dict:
        base_query = select(self.model).where(*query_params["filters"])
        total_query = select(func.count(literal_column("1"))).select_from(base_query.subquery())
        total = (await db.execute(total_query)).scalar_one()
        query = base_query
        if query_params["sort_clause"] is not None:
            query = query.order_by(query_params["sort_clause"])
        query = query.offset(query_params["offset"]).limit(query_params["limit"])
        items = (await db.execute(query)).scalars().all()
        pages = math.ceil(total / query_params["per_page"]) if query_params["per_page"] > 0 else 0
        return {"data": items,
                "pagination": {"page": query_params["page"], "per_page": query_params["per_page"], "total": total,
                               "pages": pages, "has_next": query_params["page"] < pages,
                               "has_prev": query_params["page"] > 1}}

    async def get_one(self, db: AsyncSession, item_id: int) -> Optional[ModelType]:
        instance = (await db.execute(select(self.model).where(self.model.id == item_id))).scalar_one_or_none()
        if not instance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return instance

    async def update(self, db: AsyncSession, item_id: int, data: BaseModel) -> ModelType:
        instance = await self.get_one(db, item_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, item_id: int):
        instance = await self.get_one(db, item_id)
        await db.delete(instance)
        await db.commit()

    async def search(self, db: AsyncSession, request: Request, query_params: dict) -> Dict:
        q = request.query_params.get("q", "")
        if not q: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search query 'q' required")
        fields_param = request.query_params.get("fields", "")
        search_fields = fields_param.split(',') if fields_param else [c.name for c in self.model.__table__.columns if
                                                                      hasattr(c.type, 'length')]
        conditions = [getattr(self.model, field).ilike(f'%{q}%') for field in search_fields if
                      hasattr(self.model, field)]
        query_params["filters"].extend(conditions)
        return await self.get_all(db, query_params)

    def _format_selector_label(self, item: ModelType) -> str:
        selector_cfg = self.config.selector
        if selector_cfg.display_format:
            try:
                item_dict = {c.name: getattr(item, c.name) for c in item.__table__.columns}
                return selector_cfg.display_format.format(**item_dict)
            except (KeyError, AttributeError):
                return str(item.id)
        if selector_cfg.fields: return str(getattr(item, selector_cfg.fields[0], item.id))
        return str(item.id)

    async def selector(self, db: AsyncSession, q: Optional[str]) -> List[Dict]:
        selector_cfg = self.config.selector
        query = select(self.model)
        if q and selector_cfg.search_fields:
            conditions = [getattr(self.model, field).ilike(f'%{q}%') for field in selector_cfg.search_fields]
            query = query.where(or_(*conditions))
        query = query.order_by(getattr(self.model, selector_cfg.order_by).asc()).limit(selector_cfg.limit)
        items = (await db.execute(query)).scalars().all()
        return [{"id": item.id, "value": item.id, "label": self._format_selector_label(item)} for item in items]

    async def bulk(self, db: AsyncSession, payload: BulkOperationsPayload):
        query = select(self.model).where(self.model.id.in_(payload.ids))
        items = (await db.execute(query)).scalars().all()
        if payload.operation == "delete":
            for item in items: await db.delete(item)
            msg = f"Deleted {len(items)} records successfully"
        elif payload.operation == "update":
            for item in items:
                for key, value in payload.data.items(): setattr(item, key, value)
            msg = f"Updated {len(items)} records successfully"
        await db.commit()
        return {"message": msg}


class GenericCRUDService(BaseService):
    config: CRUDConfig

    def __init__(self, router: APIRouter, db_dependency: callable = get_db):
        super().__init__(router)
        self.db_dependency = db_dependency
        self.model = self.config.model
        self.service = BaseCRUDService(model=self.model, config=self.config)
        self._register_routes()

    def _register_routes(self) -> None:
        create_schema = self.config.create_schema
        update_schema = self.config.update_schema
        response_schema = self.config.response_schema
        query_processor = QueryProcessor(model=self.model, config=self.config)
        db_dependency = self.db_dependency

        async def _validate(db: AsyncSession, data: BaseModel, item_id: Optional[int] = None):
            if not self.config.validation.unique_fields: return
            for field in self.config.validation.unique_fields:
                value = getattr(data, field, None)
                if value is not None:
                    q = select(self.model).where(getattr(self.model, field) == value)
                    if item_id: q = q.where(self.model.id != item_id)
                    if (await db.execute(q)).scalar_one_or_none():
                        raise HTTPException(status.HTTP_409_CONFLICT, f"Item with this '{field}' already exists.")

        async def dep_create(data: create_schema = Body(...), db: AsyncSession = Depends(db_dependency)):
            await _validate(db, data)

        async def dep_update(item_id: int, data: update_schema = Body(...), db: AsyncSession = Depends(db_dependency)):
            await _validate(db, data, item_id)

        ops = self.config.operations
        if ops.create:
            @self.router.post(
                "/",
                response_model=response_schema,
                status_code=status.HTTP_201_CREATED,
                dependencies=[Depends(dep_create)]
            )
            async def create(data: create_schema, db: AsyncSession = Depends(db_dependency)):
                return await self.service.create(db, data)
        if ops.list:
            @self.router.get(
                "/",
                response_model=PaginatedResponse[response_schema]
            )
            async def list_all(q_params: dict = Depends(query_processor), db: AsyncSession = Depends(db_dependency)):
                return await self.service.get_all(db, q_params)
        if ops.read:
            @self.router.get(
                "/{item_id}",
                response_model=response_schema
            )
            async def read_one(item_id: int, db: AsyncSession = Depends(db_dependency)):
                return await self.service.get_one(db, item_id)
        if ops.update:
            @self.router.put(
                "/{item_id}",
                response_model=response_schema,
                dependencies=[Depends(dep_update)]
            )
            async def update(item_id: int, data: update_schema, db: AsyncSession = Depends(db_dependency)):
                return await self.service.update(db, item_id, data)
        if ops.delete:
            @self.router.delete(
                "/{item_id}",
                status_code=status.HTTP_204_NO_CONTENT
            )
            async def delete(item_id: int, db: AsyncSession = Depends(db_dependency)):
                await self.service.delete(db, item_id)
        if ops.search:
            @self.router.get(
                "/search/",
                response_model=PaginatedResponse[response_schema]
            )
            async def search(req: Request, q_params: dict = Depends(query_processor),
                             db: AsyncSession = Depends(db_dependency)):
                return await self.service.search(db, req, q_params)
        if ops.bulk:
            @self.router.post(
                "/bulk/",
                response_model=Dict[str, str]
            )
            async def bulk(payload: BulkOperationsPayload, db: AsyncSession = Depends(db_dependency)):
                return await self.service.bulk(db, payload)
        if ops.selector:
            @self.router.get(
                "/selector/",
                response_model=List[SelectorItem]
            )
            async def selector(q: Optional[str] = None, db: AsyncSession = Depends(db_dependency)):
                return await self.service.selector(db, q)

            @self.router.get(
                "/selector/{item_id}",
                response_model=SelectorItem
            )
            async def single_selector(item_id: int, db: AsyncSession = Depends(db_dependency)):
                item = await self.service.get_one(db, item_id)
                return {"id": item.id, "value": item.id, "label": self.service._format_selector_label(item)}
