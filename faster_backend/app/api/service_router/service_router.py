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


def _normalize_path(service_name: str, path: str) -> str:
    if not path.startswith('/'):
        path = '/' + path
    # Keep {id} syntax for FastAPI
    return f'/{service_name}{path}'


class ServiceRouter:
    """FastAPI Router that auto-registers all services and creates API routes."""

    def __init__(self) -> None:
        self.router: APIRouter = APIRouter(
            prefix="/api",
            tags=["api"],
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

        self.documentation_router: 'DocumentationRouter' = DocumentationRouter(self)
        self.compact_generator: 'CompactApiGenerator' = CompactApiGenerator(self)
        self.openapi_generator: 'OpenAPIGenerator' = OpenAPIGenerator()

        self.logger.info("🚀 ServiceRouter initialized with FastAPI APIRouter")

    def register_service(self, service_name: str, service_class: type, *args, **kwargs) -> None:
        """Instantiate a service and create routes for any @expose methods."""
        try:
            self.logger.info(f"🔧 Registering service: {service_name}")

            service = service_class(*args, **kwargs)

            # Set service router reference for service integration
            service.set_service_router(self)

            self.registered_services[service_name] = service

            # Discover and register HTTP endpoints
            exposed_methods = 0
            for attr_name in dir(service):
                method = getattr(service, attr_name)
                if callable(method) and hasattr(method, '_exposed'):
                    self._create_route(service_name, method)
                    exposed_methods += 1

            self.logger.info(f"📡 Registered {exposed_methods} HTTP endpoints for {service_name}")

            self.logger.info(f"✅ Successfully registered service: {service_name}")

        except Exception as e:
            self.logger.error(f"💥 Failed to register service {service_name}: {e}")
            raise



    def _create_route(self, service_name: str, method: Callable[..., Any]) -> None:
        """Create FastAPI route for a service method."""

        # Create a proper FastAPI handler function
        def create_handler(bound_method: Callable[..., Any]) -> Callable[..., Any]:
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
        path = _normalize_path(service_name, getattr(method, '_path'))
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

    def get_service(self, service_name: str) -> BaseService | None:
        return self.registered_services.get(service_name)



    def get_router(self) -> APIRouter:
        """Get the FastAPI APIRouter instance."""
        return self.router















