from __future__ import annotations

import json
import logging
import traceback
from functools import wraps
from typing import Callable, Any

from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import Response

from .base_service import BaseService
from .documentation_router import DocumentationRouter
from .generators.compact_api_generator import CompactApiGenerator
from .generators.openapi_generator import OpenAPIGenerator
from ...config import settings


class ServiceRouter:
    """FastAPI Router that auto-registers all services and creates API routes."""

    def __init__(self) -> None:
        self.router: APIRouter = APIRouter(
            prefix="/api",
            tags=["services"],
            responses={
                400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                403: {"description": "Forbidden"},
                404: {"description": "Not Found"},
                500: {"description": "Internal Server Error"}
            }
        )
        self.registered_services: dict[str, BaseService] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._websocket_channels: dict[str, dict] = {}  # Initialize WebSocket channels dict

        self.documentation_router: 'DocumentationRouter' = DocumentationRouter(self)
        self.compact_generator: 'CompactApiGenerator' = CompactApiGenerator(self)
        self.openapi_generator: 'OpenAPIGenerator' = OpenAPIGenerator()

        # Add utility endpoints
        self._add_utility_endpoints()

        # Add WebSocket endpoints
        self._add_websocket_endpoints()

        self.logger.info("🚀 ServiceRouter initialized with FastAPI APIRouter")

    async def register_service(self, service_name: str, service_class: type, *args, **kwargs) -> None:
        """Instantiate a service and create routes for any @expose methods."""
        try:
            self.logger.info(f"🔧 Registering service: {service_name}")

            service = service_class(*args, **kwargs)

            # Set service router reference for FastAPI WebSocket support - REQUIRED!
            service.set_service_router(self)

            self.registered_services[service_name] = service

            # Discover and register HTTP endpoints
            exposed_methods = 0
            for attr_name in dir(service):
                method = getattr(service, attr_name)
                if callable(method) and hasattr(method, '_exposed'):
                    await self._create_route(service_name, method)
                    exposed_methods += 1

            self.logger.info(f"📡 Registered {exposed_methods} HTTP endpoints for {service_name}")

            # Discover and register WebSocket channels
            await self._discover_websocket_channels(service_name, service)

            self.logger.info(f"✅ Successfully registered service: {service_name}")

        except Exception as e:
            self.logger.error(f"💥 Failed to register service {service_name}: {e}")
            raise

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
        # Keep {id} syntax for FastAPI
        return f'/{service_name}{path}'

    async def _create_route(self, service_name: str, method: Callable[..., Any]) -> None:
        """Create FastAPI route for a service method."""

        # Create a proper FastAPI handler function
        async def create_handler(bound_method: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(bound_method)
            async def handler(request: Request, **kwargs):
                # Validate that required path parameters are present
                required_params = getattr(bound_method, '_required_params', [])
                missing_params = [param for param in required_params if param not in kwargs]
                if missing_params:
                    return JSONResponse(
                        status_code=400,
                        content={
                            'error': 'Missing Required Parameters',
                            'missing_params': missing_params,
                            'service': service_name,
                            'method': bound_method.__name__
                        }
                    )
                try:
                    # Enhanced logging with request details
                    self.logger.info(f"🚀 Executing {service_name}.{bound_method.__name__}")
                    self.logger.info(f"   Method: {request.method}")
                    self.logger.info(f"   URL: {request.url}")
                    self.logger.info(f"   Path Params: {kwargs}")
                    self.logger.info(f"   Query Params: {dict(request.query_params)}")
                    self.logger.info(f"   Headers: {dict(request.headers)}")

                    # Handle request body for POST/PUT/PATCH methods
                    request_body = None
                    if request.method in ['POST', 'PUT', 'PATCH']:
                        try:
                            request_body = await request.json()
                            self.logger.info(f"   Request Body: {request_body}")
                        except Exception as body_error:
                            self.logger.warning(f"Could not parse request body: {body_error}")

                    # Call the service method with the request object, parsed body, and path parameters
                    if request_body is not None:
                        result = await bound_method(request, request_body, **kwargs)
                    else:
                        result = await bound_method(request, **kwargs)

                    # Log successful execution
                    self.logger.info(f"✅ Successfully executed {service_name}.{bound_method.__name__}")

                    # Validate response format if specified
                    response_schema = getattr(bound_method, '_response_schema', None)
                    if response_schema and result is not None:
                        self.logger.debug(f"Response validation enabled for {bound_method.__name__}")
                        # Note: FastAPI will handle response validation automatically if Pydantic models are used

                    return result

                except Exception as e:
                    se = str(e)
                    self.logger.error(f"💥 CRASH in {service_name}.{bound_method.__name__}: {se}", exc_info=True)

                    # Return proper FastAPI error response with appropriate status code
                    error_content = {
                        'error': 'Service Error',
                        'service': service_name,
                        'method': bound_method.__name__,
                        'message': se
                    }

                    # Add traceback only in debug mode
                    if settings.DEBUG:
                        error_content['traceback'] = traceback.format_exc()

                    # Determine appropriate status code based on exception type
                    status_code = 500  # Default to internal server error
                    error_str = se.lower()
                    if "not found" in error_str or "does not exist" in error_str:
                        status_code = 404
                    elif "validation" in error_str or "invalid" in error_str:
                        status_code = 400
                    elif "unauthorized" in error_str or "permission" in error_str:
                        status_code = 401
                    elif "forbidden" in error_str:
                        status_code = 403

                    return JSONResponse(error_content, status_code)

            return handler

        # Create FastAPI route dynamically
        path = await self._normalize_path(service_name, getattr(method, '_path'))
        methods = getattr(method, '_methods', ['GET'])

        # Log route creation
        self.logger.info(f"🔗 Creating route: {path} for methods: {methods}")

        for method_name in methods:
            try:
                # Use add_api_route instead of ugly decorator pattern
                self.router.add_api_route(
                    path=path,
                    endpoint=create_handler(method),
                    methods=[method_name.upper()]
                )

                self.logger.info(f"✅ Registered {method_name.upper()} route: {path}")

            except Exception as route_error:
                self.logger.error(f"💥 Failed to register {method_name.upper()} route for {path}: {route_error}")
                raise

    async def list_services(self) -> list[str]:
        return list(self.registered_services.keys())

    async def get_service(self, service_name: str) -> BaseService | None:
        return self.registered_services.get(service_name)

    async def get_websocket_channels(self) -> dict[str, dict]:
        return self._websocket_channels

    def get_router(self) -> APIRouter:
        """Get the FastAPI APIRouter instance."""
        return self.router

    async def get_service_info(self, service_name: str) -> dict[str, Any] | None:
        """Get detailed information about a registered service."""
        service = self.registered_services.get(service_name)
        if not service:
            return None

        # Get exposed methods
        exposed_methods = []
        for attr_name in dir(service):
            method = getattr(service, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                method_info = {
                    'name': attr_name,
                    'path': getattr(method, '_path'),
                    'methods': getattr(method, '_methods', ['GET']),
                    'summary': getattr(method, '_summary'),
                    'description': getattr(method, '_description')
                }
                exposed_methods.append(method_info)

        return {
            'name': service_name,
            'class': service.__class__.__name__,
            'exposed_methods': exposed_methods,
            'websocket_channels': [info for info in self._websocket_channels.values() if
                                   info['service_name'] == service_name]
        }

    async def get_all_services_info(self) -> dict[str, dict[str, Any]]:
        """Get information about all registered services."""
        return {
            service_name: await self.get_service_info(service_name)
            for service_name in self.registered_services.keys()
        }

    def _add_utility_endpoints(self) -> None:
        """Add utility endpoints to the router."""

        @self.router.get("/services")
        async def list_services_endpoint():
            """List all registered services."""
            return await self.list_services()

        @self.router.get("/services/info")
        async def get_services_info_endpoint():
            """Get detailed information about all services."""
            return await self.get_all_services_info()

        @self.router.get("/services/{service_name}")
        async def get_service_info_endpoint(service_name: str):
            """Get information about a specific service."""
            service_info = await self.get_service_info(service_name)
            if not service_info:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
            return service_info

        @self.router.get("/health")
        async def health_check():
            """Health check endpoint for the service router."""
            return {
                "status": "healthy",
                "services_count": len(self.registered_services),
                "websocket_channels_count": len(self._websocket_channels),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }

        @self.router.get("/overview")
        async def get_compact_overview(services: str = None):
            """Get compact YAML overview with optional service filtering."""
            try:
                # Get optional service filter from query parameter
                service_filter = services.strip() if services else ""

                # Get the full OpenAPI spec using the existing generator
                openapi_spec = await self.openapi_generator.generate_openapi_spec(
                    self.registered_services,
                    service_filter
                )

                # Convert OpenAPI spec to compact YAML
                yaml_overview = await self.compact_generator._convert_openapi_to_compact_yaml(openapi_spec,
                                                                                              service_filter)

                return Response(
                    content=yaml_overview,
                    media_type="text/yaml",
                    headers={"Content-Type": "text/yaml"}
                )

            except Exception as exc:

                return Response(
                    content=f"# Error: {str(exc)}",
                    status_code=500,
                    media_type="text/yaml",
                    headers={"Content-Type": "text/yaml"}
                )

    def _add_websocket_endpoints(self) -> None:
        """Add WebSocket endpoints to the router."""

        @self.router.websocket("/ws/{channel}")
        async def websocket_endpoint(websocket, channel: str):
            """WebSocket endpoint for dynamic channels."""
            await self._handle_websocket_connection(websocket, channel)

        @self.router.websocket("/ws/service/{service_name}")
        async def service_websocket_endpoint(websocket, service_name: str):
            """WebSocket endpoint for service-specific channels."""
            await self._handle_service_websocket_connection(websocket, service_name)

    async def _handle_websocket_connection(self, websocket, channel: str):
        """Handle WebSocket connection for dynamic channels."""
        try:
            self.logger.info(f"🔌 WebSocket connection established for channel: {channel}")

            # Accept the connection
            await websocket.accept()

            # Store connection info
            if channel not in self._websocket_channels:
                self._websocket_channels[channel] = {
                    'connections': [],
                    'service_name': None,
                    'method_name': None
                }

            self._websocket_channels[channel]['connections'].append(websocket)

            try:
                # Keep connection alive and handle messages
                while True:
                    data = await websocket.receive_text()
                    await self._process_websocket_message(channel, data, websocket)
            except Exception as e:
                self.logger.info(f"WebSocket connection closed for channel {channel}: {e}")
            finally:
                # Clean up connection
                if channel in self._websocket_channels:
                    self._websocket_channels[channel]['connections'].remove(websocket)
                    if not self._websocket_channels[channel]['connections']:
                        del self._websocket_channels[channel]

        except Exception as e:
            self.logger.error(f"💥 WebSocket error for channel {channel}: {e}")

    async def _handle_service_websocket_connection(self, websocket, service_name: str):
        """Handle WebSocket connection for service-specific channels."""
        try:
            self.logger.info(f"🔌 Service WebSocket connection established for: {service_name}")

            # Accept the connection
            await websocket.accept()

            # Store connection info
            if service_name not in self._websocket_channels:
                self._websocket_channels[service_name] = {
                    'connections': [],
                    'service_name': service_name,
                    'method_name': None
                }

            self._websocket_channels[service_name]['connections'].append(websocket)

            try:
                # Keep connection alive and handle messages
                while True:
                    data = await websocket.receive_text()
                    await self._process_websocket_message(service_name, data, websocket)
            except Exception as e:
                self.logger.info(f"Service WebSocket connection closed for {service_name}: {e}")
            finally:
                # Clean up connection
                if service_name in self._websocket_channels:
                    self._websocket_channels[service_name]['connections'].remove(websocket)
                    if not self._websocket_channels[service_name]['connections']:
                        del self._websocket_channels[service_name]

        except Exception as e:
            self.logger.error(f"💥 Service WebSocket error for {service_name}: {e}")

    async def _process_websocket_message(self, channel: str, message: str, websocket):
        """Process incoming WebSocket message."""
        try:

            data = json.loads(message)

            # Handle different message types
            if data.get('type') == 'ping':
                await websocket.send_text(
                    json.dumps({'type': 'pong', 'timestamp': __import__('datetime').datetime.now().isoformat()}))
            elif data.get('type') == 'subscribe':
                # Handle subscription logic
                await websocket.send_text(json.dumps({'type': 'subscribed', 'channel': channel}))
            else:
                # Echo message back for now
                await websocket.send_text(json.dumps({'type': 'echo', 'message': data, 'channel': channel}))

        except Exception as e:
            self.logger.error(f"💥 Error processing WebSocket message: {e}")
            await websocket.send_text(json.dumps({'type': 'error', 'message': str(e)}))

    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast message to all connections in a channel."""
        if channel in self._websocket_channels:
            message_text = json.dumps(message)
            for websocket in self._websocket_channels[channel]['connections']:
                try:
                    await websocket.send_text(message_text)
                except Exception as e:
                    self.logger.error(f"💥 Failed to send to WebSocket: {e}")
                    # Remove dead connection
                    self._websocket_channels[channel]['connections'].remove(websocket)
