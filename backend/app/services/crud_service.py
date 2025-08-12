from __future__ import annotations

from typing import Any, Dict, List, Optional
from flask import jsonify, Request
from sqlalchemy import or_, func as sa_func

from .. import db
from ..decorators import expose


class CrudService:
    """Generic CRUD service that handles ALL operations automatically using config."""

    def __init__(self, model_class: Any | None = None, config: Optional[Dict[str, Any]] = None) -> None:
        # Model resolution: explicit arg wins; else existing attribute; else error
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

    def _call_if_enabled(self, op: str, handler, *args, **kwargs):
        if not self._is_enabled(op):
            return jsonify({'error': 'Operation disabled'}), 405
        return handler(*args, **kwargs)

    @expose('/', methods=['POST'])
    def create(self, req: Request):
        return self._call_if_enabled('create', self._handle_create, req)

    @expose('/', methods=['GET'])
    def list_all(self, req: Request):
        return self._call_if_enabled('list', self._handle_list, req)

    @expose('/{id}', methods=['GET'])
    def read_one(self, req: Request, id: int):  # noqa: A002 - id is API param name
        return self._call_if_enabled('read', self._handle_read, req, id)

    @expose('/{id}', methods=['PUT'])
    def update(self, req: Request, id: int):  # noqa: A002
        return self._call_if_enabled('update', self._handle_update, req, id)

    @expose('/{id}', methods=['DELETE'])
    def delete(self, req: Request, id: int):  # noqa: A002
        return self._call_if_enabled('delete', self._handle_delete, req, id)

    @expose('/search', methods=['GET'])
    def search(self, req: Request):
        return self._call_if_enabled('search', self._handle_search, req)

    @expose('/bulk', methods=['POST'])
    def bulk_operations(self, req: Request):
        return self._call_if_enabled('bulk', self._handle_bulk, req)

    @expose('/selector', methods=['GET'])
    def selector(self, req: Request):
        return self._call_if_enabled('selector', self._handle_selector, req)

    @expose('/selector/{id}', methods=['GET'])
    def single_selector(self, req: Request, id: int):  # noqa: A002
        return self._call_if_enabled('selector', self._handle_single_selector, req, id)

    # Handlers
    def _handle_create(self, req: Request):
        try:
            data = req.get_json(silent=True) or {}

            if self.config['validation']['enabled']:
                errors = self._validate_create_data(data)
                if errors:
                    return jsonify({'errors': errors}), 400

            instance = self.model(**data)
            db.session.add(instance)
            db.session.commit()
            return jsonify({'message': 'Created successfully', 'data': self._serialize(instance)}), 201
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    def _handle_list(self, req: Request):
        try:
            query = self.model.query

            if self.config['filters']['enabled']:
                query = self._apply_filters(query, req.args)

            if self.config['sorting']['enabled']:
                query = self._apply_sorting(query, req.args)

            if self.config['pagination']['enabled']:
                page = int(req.args.get('page', 1))
                per_page = min(
                    int(req.args.get('per_page', self.config['pagination']['default_page_size'])),
                    self.config['pagination']['max_page_size'],
                )

                pagination = query.paginate(page=page, per_page=per_page, error_out=False)
                return jsonify({
                    'data': [self._serialize(item) for item in pagination.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                    },
                })

            items = query.all()
            return jsonify({'data': [self._serialize(item) for item in items], 'total': len(items)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    def _handle_read(self, req: Request, id: int):  # noqa: A002 - id is API param name
        try:
            instance = self.model.query.filter_by(id=id).first()
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            return jsonify({'data': self._serialize(instance)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    def _handle_update(self, req: Request, id: int):  # noqa: A002
        try:
            instance = self.model.query.filter_by(id=id).first()
            if not instance:
                return jsonify({'error': 'Not found'}), 404

            data = req.get_json(silent=True) or {}
            if self.config['validation']['enabled']:
                errors = self._validate_update_data(data, instance)
                if errors:
                    return jsonify({'errors': errors}), 400

            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            db.session.commit()
            return jsonify({'message': 'Updated successfully', 'data': self._serialize(instance)})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    def _handle_delete(self, req: Request, id: int):  # noqa: A002
        try:
            instance = self.model.query.filter_by(id=id).first()
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            db.session.delete(instance)
            db.session.commit()
            return jsonify({'message': 'Deleted successfully'})
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    def _handle_search(self, req: Request):
        try:
            query_text = req.args.get('q', '')
            fields_param = req.args.get('fields', '')
            fields = [f for f in fields_param.split(',') if f] if fields_param else []

            if not query_text:
                return jsonify({'error': 'Search query required'}), 400

            base_query = self.model.query
            conditions = []
            if fields:
                for field in fields:
                    if hasattr(self.model, field):
                        conditions.append(getattr(self.model, field).ilike(f'%{query_text}%'))
            else:
                for column in self.model.__table__.columns:
                    # Heuristic: use ilike for textual columns
                    if hasattr(column.type, 'length') or column.type.python_type is str:  # type: ignore[attr-defined]
                        conditions.append(column.ilike(f'%{query_text}%'))  # type: ignore[arg-type]

            if conditions:
                base_query = base_query.filter(or_(*conditions))

            if self.config['pagination']['enabled']:
                page = int(req.args.get('page', 1))
                per_page = min(
                    int(req.args.get('per_page', self.config['pagination']['default_page_size'])),
                    self.config['pagination']['max_page_size'],
                )
                pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
                return jsonify({
                    'data': [self._serialize(item) for item in pagination.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                    },
                })

            items = base_query.all()
            return jsonify({'data': [self._serialize(item) for item in items], 'total': len(items)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    def _handle_bulk(self, req: Request):
        try:
            payload = req.get_json(silent=True) or {}
            operation = payload.get('operation')
            ids: List[int] = payload.get('ids', [])

            if not operation or not ids:
                return jsonify({'error': 'Operation and IDs required'}), 400

            if operation == 'delete':
                items = self.model.query.filter(self.model.id.in_(ids)).all()
                for item in items:
                    db.session.delete(item)
                db.session.commit()
                return jsonify({'message': f'Deleted {len(items)} records successfully'})
            elif operation == 'update':
                update_data: Dict[str, Any] = payload.get('data', {})
                items = self.model.query.filter(self.model.id.in_(ids)).all()
                for item in items:
                    for key, value in update_data.items():
                        if hasattr(item, key):
                            setattr(item, key, value)
                db.session.commit()
                return jsonify({'message': f'Updated {len(items)} records successfully'})
            else:
                return jsonify({'error': 'Invalid operation'}), 400
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    def _handle_selector(self, req: Request):
        try:
            query = self.model.query
            search_query = req.args.get('q', '')
            selector_cfg = self.config['selector']

            if search_query and selector_cfg['search_fields']:
                conditions = []
                for field_name in selector_cfg['search_fields']:
                    if hasattr(self.model, field_name):
                        conditions.append(getattr(self.model, field_name).ilike(f'%{search_query}%'))
                if conditions:
                    query = query.filter(or_(*conditions))

            order_field = selector_cfg['order_by']
            if hasattr(self.model, order_field):
                query = query.order_by(getattr(self.model, order_field).asc())

            items = query.limit(selector_cfg['limit']).all()

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

            return jsonify({'data': selector_data, 'total': len(selector_data)})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

    def _handle_single_selector(self, req: Request, id: int):  # noqa: A002
        try:
            instance = self.model.query.filter_by(id=id).first()
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            selector_item = {
                'id': getattr(instance, 'id'),
                'value': getattr(instance, 'id'),
                'label': self._format_selector_label(instance),
            }
            for field_name in self.config['selector']['fields']:
                if field_name != 'id' and hasattr(instance, field_name):
                    selector_item[field_name] = getattr(instance, field_name)
            return jsonify({'data': selector_item})
        except Exception as exc:  # noqa: BLE001
            return jsonify({'error': str(exc)}), 500

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

    def _apply_filters(self, query, args)  :  # type: ignore[no-untyped-def]
        for key, value in args.items():
            if key.startswith('filter_'):
                field_name = key[7:]
                if not hasattr(self.model, field_name):
                    continue
                field = getattr(self.model, field_name)
                if ':' in value:
                    operator, filter_value = value.split(':', 1)
                    if operator == 'eq':
                        query = query.filter(field == filter_value)
                    elif operator == 'ne':
                        query = query.filter(field != filter_value)
                    elif operator == 'gt':
                        query = query.filter(field > filter_value)
                    elif operator == 'lt':
                        query = query.filter(field < filter_value)
                    elif operator == 'like':
                        query = query.filter(field.ilike(f'%{filter_value}%'))
                    elif operator == 'in':
                        values = [v for v in filter_value.split(',') if v]
                        query = query.filter(field.in_(values))
                else:
                    query = query.filter(field == value)
        return query

    def _apply_sorting(self, query, args):  # type: ignore[no-untyped-def]
        sort_field = args.get('sort', self.config['sorting']['default_sort'])
        sort_order = args.get('order', 'asc')
        if hasattr(self.model, sort_field):
            field = getattr(self.model, sort_field)
            query = query.order_by(field.desc() if str(sort_order).lower() == 'desc' else field.asc())
        return query

    def _validate_create_data(self, data: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        for field in self.config['validation']['required_fields']:
            if field not in data or data[field] in (None, ''):
                errors.append(f'{field} is required')

        for field in self.config['validation']['unique_fields']:
            if field in data:
                existing = self.model.query.filter(getattr(self.model, field) == data[field]).first()
                if existing:
                    errors.append(f'{field} must be unique')
        return errors

    def _validate_update_data(self, data: Dict[str, Any], instance: Any) -> List[str]:
        errors: List[str] = []
        for field in self.config['validation']['unique_fields']:
            if field in data:
                existing = self.model.query.filter(
                    getattr(self.model, field) == data[field], self.model.id != instance.id
                ).first()
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

