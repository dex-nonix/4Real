from datetime import datetime, date
from typing import Type, Any

from starlette.requests import Request

from nonix_web_db.crud import CRUDConfig
from nonix_web_db.crud.types import ModelType


class QueryProcessor:
    def __init__(self, model: Type[ModelType], config: CRUDConfig):
        self.model = model
        self.config = config

    async def _coerce_value(self, field, raw_value: str) -> Any:
        try:
            column = getattr(self.model, field).property.columns[0]
            py_type = column.type.python_type
            if py_type is datetime:
                return datetime.fromisoformat(raw_value)
            if py_type is date:
                return date.fromisoformat(raw_value)
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
                op, filter_value = (
                    value.split(":", 1) if ":" in value else ("eq", value)
                )
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
                    values = [
                        await self._coerce_value(field_name, v)
                        for v in filter_value.split(",")
                    ]
                    filters.append(field.in_(values))
        sort_cfg = self.config.sorting
        sort_field_name = query_params.get("sort", sort_cfg.default_sort)
        order = query_params.get("order", "asc")
        sort_clause = None
        if sort_field_name in sort_cfg.allowed_fields:
            sort_field = getattr(self.model, sort_field_name)
            sort_clause = (
                sort_field.desc() if order.lower() == "desc" else sort_field.asc()
            )
        pag_cfg = self.config.pagination
        page = int(query_params.get("page", 1))
        per_page = min(
            int(query_params.get("per_page", pag_cfg.default_page_size)),
            pag_cfg.max_page_size,
        )
        offset = (page - 1) * per_page
        return {
            "filters": filters,
            "sort_clause": sort_clause,
            "offset": offset,
            "limit": per_page,
            "page": page,
            "per_page": per_page,
        }
