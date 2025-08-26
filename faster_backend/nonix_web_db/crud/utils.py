import math
from typing import List, Any

from fastapi import HTTPException, status
from sqlalchemy import select, func, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from .types import ModelType


def create_paginated_response(
        data: List, page: int = 1, per_page: int = 10, total: int = 0, **overrides
):
    pages = math.ceil(total / per_page) if per_page > 0 else 0
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }
    pagination.update(overrides)
    return {"data": data, "pagination": pagination}


async def execute_scalar_one(session: AsyncSession, query) -> Any:
    return (await session.execute(query)).scalar_one()


async def execute_query_all(session: AsyncSession, query) -> List[ModelType]:
    return (await session.execute(query)).scalars().all()


async def get_list_for_query_params(session, model, query_params):
    base_query = select(model).where(*query_params["filters"])
    total_query = select(func.count(literal_column("1"))).select_from(
        base_query.subquery()
    )
    total = await execute_scalar_one(session, total_query)
    query = base_query
    if query_params["sort_clause"] is not None:
        query = query.order_by(query_params["sort_clause"])
    query = query.offset(query_params["offset"]).limit(query_params["limit"])
    items = await execute_query_all(session, query)
    return create_paginated_response(
        data=items,
        page=query_params["page"],
        per_page=query_params["per_page"],
        total=total,
    )


async def get_item_by_id(session: AsyncSession, model, item_id: int) -> ModelType:
    instance = (
        await session.execute(select(model).where(model.id == item_id))
    ).scalar_one_or_none()
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )
    return instance
