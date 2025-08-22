from datetime import datetime, date
from typing import Any, Dict, List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select

from .chat_service.crud_swagger_generator import CrudSwaggerGenerator
from ...api.service_router.base_service import BaseService
from ...api.service_router.decorators import expose
from ...database import AsyncSessionLocal


class CrudService(BaseService):
    """Generic CRUD service that handles ALL operations automatically using config."""

    def __init__(self, model_class: Any | None = None, config: Optional[Dict[str, Any]] = None) -> None:
        # Model resolution: explicit arg wins; else existing attribute; else error
        super().__init__()
        if model_class is not None:
            self.model = model_class
        elif not hasattr(self, 'model'):
            raise ValueError('model is required')

        # Config resolution: explicit arg wins; else existing attribute; else error
        if config is not None:
            self.config = config
        elif not hasattr(self, 'config'):
            raise ValueError('config is required')

        # Apply default values for any missing config keys (no generic fallback when entirely missing)
        self.config = self._apply_default_config_values(self.config)

    def _apply_default_config_values(self, provided_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fill in only missing keys from the default config; keep provided values as-is.

        This does NOT create a config if none was provided; caller must supply one.
        """
        defaults = self._get_default_config()

        def merge(dst: Dict[str, Any], src_defaults: Dict[str, Any]) -> Dict[str, Any]:
            for key, def_value in src_defaults.items():
                if key not in dst:
                    dst[key] = def_value
                else:
                    cur_value = dst[key]
                    if isinstance(cur_value, dict) and isinstance(def_value, dict):
                        dst[key] = merge(cur_value, def_value)
            return dst

        return merge(dict(provided_config), defaults)

    async def to_swagger(self, service_name: str = None) -> Dict[str, Any]:
        """Generate Swagger documentation for CRUD operations from model + config."""

        # Validate service_name immediately (no default, no fallback)
        if not service_name:
            raise ValueError("service_name is required for CRUD service Swagger generation")

        # Use the CrudSwaggerGenerator to handle all Swagger generation
        generator = CrudSwaggerGenerator(self, service_name)
        return await generator.generate_swagger(service_name)

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'operations': {
                'create': True,
                'read': True,
                'update': True,
                'delete': True,
                'list': True,
                'search': True,
                'bulk': True,
                'selector': True,
            },
            'filters': {
                'enabled': True,
                'fields': [],
                'operators': ['eq', 'ne', 'gt', 'lt', 'like', 'in'],
            },
            'pagination': {
                'enabled': True,
                'default_page_size': 20,
                'max_page_size': 100,
            },
            'sorting': {
                'enabled': True,
                'default_sort': 'id',
                'allowed_fields': [],
            },
            'validation': {
                'enabled': True,
                'required_fields': [],
                'unique_fields': [],
            },
            'selector': {
                'enabled': True,
                'fields': ['name'],  # Extra fields; 'id' is always included
                'display_format': None,
                'search_fields': ['name'],
                'limit': 100,
                'order_by': 'name',
            },
        }

    # Explicit decorated methods; disabled ops return 405
    def _is_enabled(self, op: str) -> bool:
        return bool(self.config.get('operations', {}).get(op, False))

    async def _call_if_enabled(self, op: str, handler, *args, **kwargs):
        if not self._is_enabled(op):
            return JSONResponse({'error': 'Operation disabled'}, 405)
        return await handler(*args, **kwargs)

    @expose('/', methods=['POST'])
    async def create(self, req: Request):
        return await self._call_if_enabled('create', self._handle_create, req)

    @expose('/', methods=['GET'])
    async def list_all(self, req: Request):
        return await self._call_if_enabled('list', self._handle_list, req)

    @expose('/{id}', methods=['GET'])
    async def read_one(self, req: Request, id: int):  # noqa: A002 - id is API param name
        return await self._call_if_enabled('read', self._handle_read, req, id)

    @expose('/{id}', methods=['PUT'])
    async def update(self, req: Request, id: int):  # noqa: A002
        return await self._call_if_enabled('update', self._handle_update, req, id)

    @expose('/{id}', methods=['DELETE'])
    async def delete(self, req: Request, id: int):  # noqa: A002
        return await self._call_if_enabled('delete', self._handle_delete, req, id)

    @expose('/search', methods=['GET'])
    async def search(self, req: Request):
        return await self._call_if_enabled('search', self._handle_search, req)

    @expose('/bulk', methods=['POST'])
    async def bulk_operations(self, req: Request):
        return await self._call_if_enabled('bulk', self._handle_bulk, req)

    @expose('/selector', methods=['GET'])
    async def selector(self, req: Request):
        return await self._call_if_enabled('selector', self._handle_selector, req)

    @expose('/selector/{id}', methods=['GET'])
    async def single_selector(self, req: Request, id: int):  # noqa: A002
        return await self._call_if_enabled('selector', self._handle_single_selector, req, id)

    # Handlers
    async def _handle_create(self, req: Request):
        try:
            data = await req.json()

            if self.config['validation']['enabled']:
                errors = await self._validate_create_data(data)
                if errors:
                    return JSONResponse({'errors': errors}, 400)

            async with AsyncSessionLocal() as session:
                instance = self.model(**data)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return JSONResponse({'message': 'Created successfully', 'data': self._serialize(instance)}, 201)
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_list(self, req: Request):
        try:
            async with AsyncSessionLocal() as session:
                query = select(self.model)

                if self.config['filters']['enabled']:
                    query = await self._apply_filters(query, req.query_params)

                if self.config['sorting']['enabled']:
                    query = self._apply_sorting(query, req.query_params)

                if self.config['pagination']['enabled']:
                    page = int(req.query_params.get('page', 1))
                    per_page = min(
                        int(req.query_params.get('per_page', self.config['pagination']['default_page_size'])),
                        self.config['pagination']['max_page_size'],
                    )

                    # Manual pagination with async SQLAlchemy
                    offset = (page - 1) * per_page
                    query = query.offset(offset).limit(per_page)

                    result = await session.execute(query)
                    items = result.scalars().all()

                    # Get total count
                    count_query = select(self.model)
                    if self.config['filters']['enabled']:
                        count_query = await self._apply_filters(count_query, req.query_params)
                    count_result = await session.execute(count_query)
                    total = len(count_result.scalars().all())

                    serialized_items = [self._serialize(item) for item in items]
                    pages = (total + per_page - 1) // per_page

                    return {
                        'data': serialized_items,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'pages': pages,
                            'has_next': page < pages,
                            'has_prev': page > 1,
                        },
                    }

            result = await session.execute(query)
            items = result.scalars().all()
            serialized_items = [self._serialize(item) for item in items]
            return JSONResponse({'data': serialized_items, 'total': len(items)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_read(self, req: Request, id: int):  # noqa: A002 - id is API param name
        try:
            async with AsyncSessionLocal() as session:
                query = select(self.model).where(self.model.id == id)
                result = await session.execute(query)
                instance = result.scalar_one_or_none()

                if not instance:
                    return JSONResponse({'error': 'Not found'}, 404)
                return JSONResponse({'data': self._serialize(instance)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_update(self, req: Request, id: int):  # noqa: A002
        try:
            async with AsyncSessionLocal() as session:
                query = select(self.model).where(self.model.id == id)
                result = await session.execute(query)
                instance = result.scalar_one_or_none()

                if not instance:
                    return JSONResponse({'error': 'Not found'}, 404)

                data = await req.json()
                if self.config['validation']['enabled']:
                    errors = await self._validate_update_data(data, instance)
                    if errors:
                        return JSONResponse({'errors': errors}, 400)

                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)

                await session.commit()
                return JSONResponse({'message': 'Updated successfully', 'data': self._serialize(instance)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_delete(self, req: Request, id: int):  # noqa: A002
        try:
            async with AsyncSessionLocal() as session:
                query = select(self.model).where(self.model.id == id)
                result = await session.execute(query)
                instance = result.scalar_one_or_none()

                if not instance:
                    return JSONResponse({'error': 'Not found'}, 404)

                await session.delete(instance)
                await session.commit()
                return JSONResponse({'message': 'Deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_search(self, req: Request):
        try:
            async with AsyncSessionLocal() as session:
                query_text = req.query_params.get('q', '')
                fields_param = req.query_params.get('fields', '')
                fields = [f for f in fields_param.split(',') if f] if fields_param else []

                if not query_text:
                    return JSONResponse({'error': 'Search query required'}, 400)

                base_query = select(self.model)
                conditions = []
                if fields:
                    for field in fields:
                        if hasattr(self.model, field):
                            conditions.append(getattr(self.model, field).ilike(f'%{query_text}%'))
                else:
                    for column in self.model.__table__.columns:
                        # Heuristic: use ilike for textual columns
                        if hasattr(column.type,
                                   'length') or column.type.python_type is str:  # type: ignore[attr-defined]
                            conditions.append(column.ilike(f'%{query_text}%'))  # type: ignore[arg-type]

                if conditions:
                    base_query = base_query.where(or_(*conditions))

                if self.config['pagination']['enabled']:
                    page = int(req.query_params.get('page', 1))
                    per_page = min(
                        int(req.query_params.get('per_page', self.config['pagination']['default_page_size'])),
                        self.config['pagination']['max_page_size'],
                    )

                    # Manual pagination with async SQLAlchemy
                    offset = (page - 1) * per_page
                    paginated_query = base_query.offset(offset).limit(per_page)

                    result = await session.execute(paginated_query)
                    items = result.scalars().all()

                    # Get total count
                    count_result = await session.execute(base_query)
                    total = len(count_result.scalars().all())
                    pages = (total + per_page - 1) // per_page

                    serialized_items = [self._serialize(item) for item in items]
                    return {
                        'data': serialized_items,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'pages': pages,
                        },
                    }

                result = await session.execute(base_query)
                items = result.scalars().all()
                serialized_items = [self._serialize(item) for item in items]
                return JSONResponse({'data': serialized_items, 'total': len(items)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_bulk(self, req: Request):
        try:
            async with AsyncSessionLocal() as session:
                payload = await req.json()
                operation = payload.get('operation')
                ids: List[int] = payload.get('ids', [])

                if not operation or not ids:
                    return JSONResponse({'error': 'Operation and IDs required'}, 400)

                if operation == 'delete':
                    query = select(self.model).where(self.model.id.in_(ids))
                    result = await session.execute(query)
                    items = result.scalars().all()

                    for item in items:
                        await session.delete(item)
                    await session.commit()
                    return JSONResponse({'message': f'Deleted {len(items)} records successfully'})
                elif operation == 'update':
                    update_data: Dict[str, Any] = payload.get('data', {})
                    query = select(self.model).where(self.model.id.in_(ids))
                    result = await session.execute(query)
                    items = result.scalars().all()

                    for item in items:
                        for key, value in update_data.items():
                            if hasattr(item, key):
                                setattr(item, key, value)
                    await session.commit()
                    return JSONResponse({'message': f'Updated {len(items)} records successfully'})
                else:
                    return JSONResponse({'error': 'Invalid operation'}, 400)
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_selector(self, req: Request):
        try:
            async with AsyncSessionLocal() as session:
                query = select(self.model)
                search_query = req.query_params.get('q', '')
                selector_cfg = self.config['selector']

                if search_query and selector_cfg['search_fields']:
                    conditions = []
                    for field_name in selector_cfg['search_fields']:
                        if hasattr(self.model, field_name):
                            conditions.append(getattr(self.model, field_name).ilike(f'%{search_query}%'))
                    if conditions:
                        query = query.where(or_(*conditions))

                order_field = selector_cfg['order_by']
                if hasattr(self.model, order_field):
                    query = query.order_by(getattr(self.model, order_field).asc())

                query = query.limit(selector_cfg['limit'])
                result = await session.execute(query)
                items = result.scalars().all()

                selector_data = []
                for item in items:
                    selector_item = {
                        'id': getattr(item, 'id'),
                        'value': getattr(item, 'id'),
                        'label': self._format_selector_label(item),
                    }
                    for field_name in selector_cfg['fields']:
                        if field_name != 'id' and hasattr(item, field_name):
                            selector_item[field_name] = getattr(item, field_name)
                    selector_data.append(selector_item)

                return JSONResponse({'data': selector_data, 'total': len(selector_data)})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    async def _handle_single_selector(self, req: Request, id: int):  # noqa: A002
        try:
            async with AsyncSessionLocal() as session:
                query = select(self.model).where(self.model.id == id)
                result = await session.execute(query)
                instance = result.scalar_one_or_none()

                if not instance:
                    return JSONResponse({'error': 'Not found'}, 404)

                selector_item = {
                    'id': getattr(instance, 'id'),
                    'value': getattr(instance, 'id'),
                    'label': self._format_selector_label(instance),
                }
                for field_name in self.config['selector']['fields']:
                    if field_name != 'id' and hasattr(instance, field_name):
                        selector_item[field_name] = getattr(instance, field_name)
                return JSONResponse({'data': selector_item})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({'error': str(exc)}, 500)

    # Helpers
    def _format_selector_label(self, item: Any) -> str:
        display_format: Optional[str] = self.config['selector'].get('display_format')
        if display_format:
            label = display_format
            for field_name in self.config['selector']['fields']:
                if field_name != 'id' and hasattr(item, field_name):
                    label = label.replace(field_name, str(getattr(item, field_name)))
            label = label.replace(' + " " + ', ' ')
            return label.strip()

        for field_name in self.config['selector']['fields']:
            if field_name != 'id' and hasattr(item, field_name):
                return str(getattr(item, field_name))
        return str(getattr(item, 'id'))

    async def _apply_filters(self, query, args):  # type: ignore[no-untyped-def]
        for key, value in args.items():
            if key.startswith('filter_'):
                field_name = key[7:]
                if not hasattr(self.model, field_name):
                    continue
                field = getattr(self.model, field_name)
                if ':' in value:
                    operator, filter_value = value.split(':', 1)
                    if operator == 'eq':
                        query = query.filter(field == await self._coerce_value(field, filter_value))
                    elif operator == 'ne':
                        query = query.filter(field != await self._coerce_value(field, filter_value))
                    elif operator == 'gt':
                        query = query.filter(field > await self._coerce_value(field, filter_value))
                    elif operator == 'lt':
                        query = query.filter(field < await self._coerce_value(field, filter_value))
                    elif operator == 'like':
                        query = query.filter(field.ilike(f'%{filter_value}%'))
                    elif operator == 'in':
                        values = [await self._coerce_value(field, v) for v in filter_value.split(',') if v]
                        query = query.filter(field.in_(values))
                    elif operator == 'between':
                        parts = [p for p in filter_value.split(',') if p]
                        if len(parts) >= 2:
                            low = await self._coerce_value(field, parts[0])
                            high = await self._coerce_value(field, parts[1])
                            query = query.filter(field.between(low, high))
                else:
                    query = query.filter(field == await self._coerce_value(field, value))
        return query

    async def _coerce_value(self, field, raw: str):  # type: ignore[no-untyped-def]
        """Best-effort coercion of string filter values to the column's python_type."""
        try:
            column = field.property.columns[0]
            py_type = getattr(column.type, 'python_type', None)
        except Exception:  # noqa: BLE001
            py_type = None

        if py_type is None or py_type is str:
            return raw

        # Datetime/date handling
        try:
            if py_type is datetime:
                return datetime.fromisoformat(raw)
            if py_type is date:
                return date.fromisoformat(raw)
        except Exception:  # noqa: BLE001
            pass

        # Generic cast
        try:
            return py_type(raw)  # type: ignore[call-arg]
        except Exception:  # noqa: BLE001
            return raw

    def _apply_sorting(self, query, args):  # type: ignore[no-untyped-def]
        sort_field = args.get('sort', self.config['sorting']['default_sort'])
        sort_order = args.get('order', 'asc')
        if hasattr(self.model, sort_field):
            field = getattr(self.model, sort_field)
            query = query.order_by(field.desc() if str(sort_order).lower() == 'desc' else field.asc())
        return query

    async def _validate_create_data(self, data: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        for field in self.config['validation']['required_fields']:
            if field not in data or data[field] in (None, ''):
                errors.append(f'{field} is required')

        for field in self.config['validation']['unique_fields']:
            if field in data:
                async with AsyncSessionLocal() as session:
                    query = select(self.model).where(getattr(self.model, field) == data[field])
                    result = await session.execute(query)
                    existing = result.scalar_one_or_none()
                    if existing:
                        errors.append(f'{field} must be unique')
        return errors

    async def _validate_update_data(self, data: Dict[str, Any], instance: Any) -> List[str]:
        errors: List[str] = []
        for field in self.config['validation']['unique_fields']:
            if field in data:
                async with AsyncSessionLocal() as session:
                    query = select(self.model).where(
                        getattr(self.model, field) == data[field],
                        self.model.id != instance.id
                    )
                    result = await session.execute(query)
                    existing = result.scalar_one_or_none()
                    if existing:
                        errors.append(f'{field} must be unique')
        return errors

    def _serialize(self, instance: Any) -> Dict[str, Any]:
        if hasattr(instance, 'to_dict'):
            return instance.to_dict()
        result: Dict[str, Any] = {}
        for column in instance.__table__.columns:  # type: ignore[attr-defined]
            result[column.name] = getattr(instance, column.name)
        return result
