from __future__ import annotations

from flask import Blueprint, request
from functools import wraps
from typing import Any, Callable


class APIRouter:
    """Blueprint that auto-registers all services by discovering @expose methods."""

    def __init__(self) -> None:
        self.blueprint = Blueprint('api', __name__)
        self.registered_services: dict[str, Any] = {}

    def register_service(self, service_name: str, service_class: type, *args: Any, **kwargs: Any) -> None:
        """Instantiate a service and create routes for any @expose methods."""
        service = service_class(*args, **kwargs)
        self.registered_services[service_name] = service

        for attr_name in dir(service):
            method = getattr(service, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                self._create_route(service_name, method)

    def register_service_factory(self, service_name: str, factory: Callable[[], Any]) -> None:
        service = factory()
        self.registered_services[service_name] = service

        for attr_name in dir(service):
            method = getattr(service, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                self._create_route(service_name, method)

    def _normalize_path(self, service_name: str, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        # Convert `{id}` style placeholders to Flask `<id>`
        flask_path = path.replace('{', '<').replace('}', '>')
        return f'/{service_name}{flask_path}'

    def _create_route(self, service_name: str, method: Callable) -> None:
        full_path = self._normalize_path(service_name, getattr(method, '_path'))
        methods = getattr(method, '_methods', ['GET'])

        # Bind the current method into the handler's defaults to avoid late-binding issues
        def handler_factory(bound_method: Callable) -> Callable:
            @wraps(bound_method)
            def handler(**kwargs: Any):
                return bound_method(request, **kwargs)

            return handler

        endpoint = f"{service_name}:{getattr(method, '__name__', 'endpoint')}:{full_path}"
        self.blueprint.add_url_rule(full_path, endpoint=endpoint, view_func=handler_factory(method), methods=methods)

    def list_services(self) -> list[str]:
        return list(self.registered_services.keys())

    def get_service(self, service_name: str) -> Any | None:
        return self.registered_services.get(service_name)

