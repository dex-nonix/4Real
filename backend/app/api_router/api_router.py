from __future__ import annotations

from flask import Blueprint, request, current_app, jsonify
from functools import wraps
from typing import Any, Callable
import logging
import traceback
import sys

from .documentation_router import DocumentationRouter

class APIRouter:
    """Blueprint that auto-registers all services and creates API routes."""

    _instance = None

    def __init__(self) -> None:
        self.blueprint = Blueprint('api', __name__)
        self.registered_services: dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Add documentation routes
        self.documentation_router = DocumentationRouter(self.blueprint)
        
        # Store instance for documentation access
        APIRouter._instance = self

    @classmethod
    def get_instance(cls):
        """Get the current instance of APIRouter"""
        return cls._instance











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
                try:
                    # Log the execution start
                    exec_msg = f"🚀 Executing {service_name}.{bound_method.__name__} with kwargs: {kwargs}"
                    print(f"\n{exec_msg}")
                    sys.stdout.flush()
                    self.logger.info(exec_msg)
                    
                    result = bound_method(request, **kwargs)
                    
                    # Log successful execution
                    success_msg = f"✅ Successfully executed {service_name}.{bound_method.__name__}"
                    print(f"{success_msg}")
                    sys.stdout.flush()
                    self.logger.info(success_msg)
                    
                    return result
                    
                except Exception as e:
                    # IMMEDIATE ERROR OUTPUT TO TERMINAL
                    error_msg = f"💥 CRASH in {service_name}.{bound_method.__name__}: {str(e)}"
                    traceback_msg = f"📋 Full Traceback:\n{traceback.format_exc()}"
                    
                    # Print to terminal immediately with colors
                    print(f"\n\033[91m{error_msg}\033[0m", file=sys.stderr)
                    print(f"\033[91m{traceback_msg}\033[0m", file=sys.stderr)
                    sys.stderr.flush()
                    
                    # Also log normally
                    self.logger.error(error_msg)
                    self.logger.error(traceback_msg)
                    
                    # Return a proper error response
                    from flask import jsonify
                    return jsonify({
                        'error': 'Service Error',
                        'service': service_name,
                        'method': bound_method.__name__,
                        'message': str(e),
                        'traceback': traceback.format_exc() if current_app.config.get('DEBUG') else None
                    }), 500

            return handler

        endpoint = f"{service_name}:{getattr(method, '__name__', 'endpoint')}:{full_path}"
        self.blueprint.add_url_rule(full_path, endpoint=endpoint, view_func=handler_factory(method), methods=methods)

    def list_services(self) -> list[str]:
        return list(self.registered_services.keys())

    def get_service(self, service_name: str) -> Any | None:
        return self.registered_services.get(service_name)

