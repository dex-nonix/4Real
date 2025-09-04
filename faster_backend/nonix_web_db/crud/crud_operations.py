from typing import TypeVar, Generic, Type, List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from fastapi import HTTPException, status
from pydantic import BaseModel
from .models_and_schemas import CRUDConfig

from .utils import execute_query_all, create_paginated_response, get_item_by_id

ModelType = TypeVar("ModelType")

# needs to be the service
class CRUDOperations(Generic[ModelType]):
    model: Type[ModelType]
    config: CRUDConfig

    def __init__(self, model: Type[ModelType] = None, config: CRUDConfig = None):
        if model:
            self.model = model
        if config:
            self.config = config

    async def create(self, data: BaseModel, session: AsyncSession) -> ModelType:
        await self._validate_unique_fields(data, None, session)
        instance = self.model(**data.model_dump())
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def update(self, item_id: int, data: BaseModel, session: AsyncSession) -> ModelType:
        await self._validate_unique_fields(data, item_id, session)
        update_data = data.model_dump(exclude_unset=True)
        
        stmt = update(self.model).where(self.model.id == item_id).values(**update_data)
        await session.execute(stmt)
        await session.commit()
        
        return await self.get_one(item_id, session)

    async def delete(self, item_id: int, session: AsyncSession):
        # Fetch to preserve 404 semantics when not found
        instance = await get_item_by_id(session, self.model, item_id)
        await session.delete(instance)
        await session.commit()

    async def get_one(self, item_id: int, session: AsyncSession) -> ModelType:
        # Use shared util to preserve HTTP 404 behavior
        return await get_item_by_id(session, self.model, item_id)

    async def get_all(self, query_params: dict, session: AsyncSession) -> Dict:
        query = select(self.model)
        
        # Apply auto-filters from context
        if self.config.filters.context_aware and "context" in query_params:
            context = query_params["context"]
            for field_name, context_key in self.config.filters.auto_filters.items():
                if context_key in context:
                    field = getattr(self.model, field_name)
                    query = query.where(field == context[context_key])
        
        # Apply default filters
        for field_name, default_value in self.config.filters.default_filters.items():
            if default_value == "required" and "context" in query_params:
                # For required fields, get from context
                context = query_params["context"]
                # Check if the field exists in context (either directly or via auto_filters mapping)
                context_key = self.config.filters.auto_filters.get(field_name, field_name)
                if context_key in context:
                    field = getattr(self.model, field_name)
                    query = query.where(field == context[context_key])
            elif default_value != "required":
                # For static default values
                field = getattr(self.model, field_name)
                query = query.where(field == default_value)
        
        # Apply manual filters
        if "filters" in query_params:
            for filter_condition in query_params["filters"]:
                query = query.where(filter_condition)
        
        # Apply field-based filters (e.g., filter_title=value, filter_artist_id=123)
        for key, value in query_params.items():
            if key.startswith("filter_") and value is not None:
                field_name = key[7:]  # Remove "filter_" prefix
                
                # Check if field filtering is allowed
                if (self.config.filters.strict_filtering and 
                    self.config.filters.allowed_fields and 
                    field_name not in self.config.filters.allowed_fields):
                    continue  # Skip this filter if strict filtering is enabled
                
                # Apply the filter
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    if isinstance(value, str) and ":" in value:
                        # Handle special filter operations like "like", "in", "gt", etc.
                        operation, filter_value = value.split(":", 1)
                        if operation == "like":
                            query = query.where(field.ilike(f"%{filter_value}%"))
                        elif operation == "in":
                            filter_values = filter_value.split(",")
                            query = query.where(field.in_(filter_values))
                        elif operation == "gt":
                            query = query.where(field > filter_value)
                        elif operation == "lt":
                            query = query.where(field < filter_value)
                        elif operation == "gte":
                            query = query.where(field >= filter_value)
                        elif operation == "lte":
                            query = query.where(field <= filter_value)
                        elif operation == "ne":
                            query = query.where(field != filter_value)
                        else:
                            # Default to equality
                            query = query.where(field == filter_value)
                    else:
                        # Simple equality filter
                        query = query.where(field == value)
        
        # Handle sorting
        order_by = query_params.get("order_by", self.config.sorting.default_sort)
        if order_by:
            # Parse order_by parameter (e.g., "field:direction" or just "field")
            if ":" in order_by:
                field_name, direction = order_by.split(":", 1)
                direction = direction.lower()
            else:
                field_name = order_by
                direction = "asc"
            
            # Validate field exists and is allowed for sorting
            if hasattr(self.model, field_name):
                if not self.config.sorting.allowed_fields or field_name in self.config.sorting.allowed_fields:
                    field = getattr(self.model, field_name)
                    if direction == "desc":
                        query = query.order_by(field.desc())
                    else:
                        query = query.order_by(field.asc())
                else:
                    # Use default sorting if field not allowed
                    default_field = getattr(self.model, self.config.sorting.default_sort)
                    query = query.order_by(default_field.asc())
            else:
                # Use default sorting if field doesn't exist
                default_field = getattr(self.model, self.config.sorting.default_sort)
                query = query.order_by(default_field.asc())
        else:
            # Apply default sorting
            default_field = getattr(self.model, self.config.sorting.default_sort)
            query = query.order_by(default_field.asc())
        
        total_count = await self._get_count(session, query_params)
        
        # Handle pagination
        page = query_params.get("page", 1)
        per_page = query_params.get("per_page", self.config.pagination.default_page_size)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < self.config.pagination.min_page_size:
            per_page = self.config.pagination.min_page_size
        if per_page > self.config.pagination.max_page_size:
            per_page = self.config.pagination.max_page_size
        
        # Convert to offset/limit
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        items = await execute_query_all(session, query)
        return create_paginated_response(
            data=items,
            page=query_params.get("page", 1),
            per_page=query_params.get("per_page", 10),
            total=total_count
        )

    async def bulk_update(self, ids: List[int], data: dict, session: AsyncSession):
        stmt = update(self.model).where(self.model.id.in_(ids)).values(**data)
        await session.execute(stmt)
        await session.commit()

    async def _validate_unique_fields(self, data: BaseModel, item_id: Optional[int], session: AsyncSession):
        if not self.config.validation.unique_fields:
            return
            
        for field_name in self.config.validation.unique_fields:
            field_value = getattr(data, field_name, None)
            if field_value is None:
                continue
                
            query = select(self.model).where(getattr(self.model, field_name) == field_value)
            if item_id is not None:
                query = query.where(self.model.id != item_id)
                
            result = await session.execute(query)
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Item with this '{field_name}' already exists."
                )

    async def _get_count(self, session: AsyncSession, query_params: dict) -> int:
        query = select(self.model)
        
        # Apply auto-filters from context (same logic as get_all)
        if self.config.filters.context_aware and "context" in query_params:
            context = query_params["context"]
            for field_name, context_key in self.config.filters.auto_filters.items():
                if context_key in context:
                    field = getattr(self.model, field_name)
                    query = query.where(field == context[context_key])
        
        # Apply default filters
        for field_name, default_value in self.config.filters.default_filters.items():
            if default_value == "required" and "context" in query_params:
                context = query_params["context"]
                # Check if the field exists in context (either directly or via auto_filters mapping)
                context_key = self.config.filters.auto_filters.get(field_name, field_name)
                if context_key in context:
                    field = getattr(self.model, field_name)
                    query = query.where(field == context[context_key])
            elif default_value != "required":
                field = getattr(self.model, field_name)
                query = query.where(field == default_value)
        
        # Apply manual filters
        if "filters" in query_params:
            for filter_condition in query_params["filters"]:
                query = query.where(filter_condition)
        
        # Apply field-based filters (same logic as get_all)
        for key, value in query_params.items():
            if key.startswith("filter_") and value is not None:
                field_name = key[7:]  # Remove "filter_" prefix
                
                # Check if field filtering is allowed
                if (self.config.filters.strict_filtering and 
                    self.config.filters.allowed_fields and 
                    field_name not in self.config.filters.allowed_fields):
                    continue  # Skip this filter if strict filtering is enabled
                
                # Apply the filter
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    if isinstance(value, str) and ":" in value:
                        # Handle special filter operations like "like", "in", "gt", etc.
                        operation, filter_value = value.split(":", 1)
                        if operation == "like":
                            query = query.where(field.ilike(f"%{filter_value}%"))
                        elif operation == "in":
                            filter_values = filter_value.split(",")
                            query = query.where(field.in_(filter_values))
                        elif operation == "gt":
                            query = query.where(field > filter_value)
                        elif operation == "lt":
                            query = query.where(field < filter_value)
                        elif operation == "gte":
                            query = query.where(field >= filter_value)
                        elif operation == "lte":
                            query = query.where(field <= filter_value)
                        elif operation == "ne":
                            query = query.where(field != filter_value)
                        else:
                            # Default to equality
                            query = query.where(field == filter_value)
                    else:
                        # Simple equality filter
                        query = query.where(field == value)
        
        # Don't apply pagination to count query, but apply sorting for consistency
        order_by = query_params.get("order_by", self.config.sorting.default_sort)
        if order_by:
            if ":" in order_by:
                field_name, direction = order_by.split(":", 1)
                direction = direction.lower()
            else:
                field_name = order_by
                direction = "asc"
            
            if hasattr(self.model, field_name):
                if not self.config.sorting.allowed_fields or field_name in self.config.sorting.allowed_fields:
                    field = getattr(self.model, field_name)
                    if direction == "desc":
                        query = query.order_by(field.desc())
                    else:
                        query = query.order_by(field.asc())
        
        stmt = select(func.count()).select_from(query.subquery())
        result = await session.execute(stmt)
        return result.scalar()

    async def search(self, query_params: dict, search_query: str, session: AsyncSession) -> Dict:
        if not search_query:
            return create_paginated_response(data=[], page=1, per_page=10, total=0)
        
        fields_param = query_params.get("fields", "")
        search_fields = (
            fields_param.split(",") if fields_param else
            [c.name for c in self.model.__table__.columns if hasattr(c.type, "length")]
        )
        
        conditions = [
            getattr(self.model, field).ilike(f"%{search_query}%")
            for field in search_fields
            if hasattr(self.model, field)
        ]
        
        if conditions:
            query_params["filters"] = query_params.get("filters", []) + conditions
        
        return await self.get_all(query_params, session)

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

    async def selector(self, q: Optional[str], session: AsyncSession) -> List[Dict]:
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

    async def single_selector(self, item_id: int, session: AsyncSession) -> Dict:
        item = await self.get_one(item_id, session)
        return {
            "id": item.id,
            "value": item.id,
            "label": self._format_selector_label(item),
        }
