from __future__ import annotations

import logging
import traceback
from functools import wraps
from typing import Callable, Any

from flask import Blueprint, request, current_app
from fastapi.responses import JSONResponse

from .base_service import BaseService
from .generators.compact_api_generator import CompactApiGenerator
from .documentation_router import DocumentationRouter



class ServiceRouter:
    """Blueprint that auto-registers all services and creates API routes."""

    def __init__(self, socketio_instance: Any = None) -> None:
        self.blueprint: Blueprint = Blueprint('api', __name__)
        self.registered_services: dict[str, BaseService] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.socketio: Any = socketio_instance  # Store SocketIO instance for WebSocket support
        self._websocket_channels: dict[str, dict] = {}  # Initialize WebSocket channels dict

        self.documentation_router: 'DocumentationRouter' = DocumentationRouter(self)
        self.compact_generator: 'CompactApiGenerator' = CompactApiGenerator(self)

    async def register_service(self, service_name: str, service_class: type, *args, **kwargs) -> None:
        """Instantiate a service and create routes for any @expose methods."""
        service = service_class(*args, **kwargs)

        await service.set_socketio(self.socketio)

        self.registered_services[service_name] = service

        # Discover and register HTTP endpoints
        for attr_name in dir(service):
            method = getattr(service, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                await self._create_route(service_name, method)

        # Discover and register WebSocket channels
        await self._discover_websocket_channels(service_name, service)

    async def _discover_websocket_channels(self, service_name: str, service: BaseService) -> None:
        """Discover @expose_ws methods and register WebSocket channels."""
        ws_methods = await service.get_exposed_ws_methods()

        for method_info in ws_methods:
            self.logger.info(
                f"🔌 Registered WebSocket channel: {service_name}.{method_info['name']} -> {method_info['channel']}")

            # Store WebSocket method info
            self._websocket_channels[method_info['channel']] = {
                'service_name': service_name,
                'method_name': method_info['name'],
                'service': service
            }

    async def _normalize_path(self, service_name: str, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        # Convert `{id}` style placeholders to Flask `<id>`
        flask_path = path.replace('{', '<').replace('}', '>')
        return f'/{service_name}{flask_path}'

    async def _create_route(self, service_name: str, method: Callable[..., Any]) -> None:

        # Bind the current method into the handler's defaults to avoid late-binding issues
        async def handler_factory(bound_method: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(bound_method)
            async def handler(**kwargs):
                try:
                    # Log the execution start
                    self.logger.info(f"🚀 Executing {service_name}.{bound_method.__name__} with kwargs: {kwargs}")
                    result = await bound_method(request, **kwargs)
                    # Log successful execution
                    self.logger.info(f"✅ Successfully executed {service_name}.{bound_method.__name__}")
                    return result

                except Exception as e:
                    self.logger.error(f"💥 CRASH in {service_name}.{bound_method.__name__}: {str(e)}", exc_info=True)

                    return JSONResponse({
                        'error': 'Service Error',
                        'service': service_name,
                        'method': bound_method.__name__,
                        'message': str(e),
                        'traceback': traceback.format_exc() if current_app.config.get('DEBUG') else None
                    },500)

            return handler

        self.blueprint.add_url_rule(
            await self._normalize_path(service_name, getattr(method, '_path')),
            endpoint=f"{service_name}:{getattr(method, '__name__', 'endpoint')}:{await self._normalize_path(service_name, getattr(method, '_path'))}",
            view_func=await handler_factory(method),
            methods=getattr(method, '_methods', ['GET'])
        )

    async def list_services(self) -> list[str]:
        return list(self.registered_services.keys())

    async def get_service(self, service_name: str) -> BaseService | None:
        return self.registered_services.get(service_name)

    async def get_websocket_channels(self) -> dict[str, dict]:
        return self._websocket_channels
