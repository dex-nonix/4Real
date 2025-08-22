from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING



if TYPE_CHECKING:
    from .service_router import ServiceRouter

from .generators.openapi_generator import OpenAPIGenerator
from .generators.swagger_ui_generator import SwaggerUIGenerator


class DocumentationRouter:
    """Handles documentation-related routes and endpoints."""

    def __init__(self, router: 'ServiceRouter') -> None:
        self.router: 'ServiceRouter' = router
        self.fastapi_router = router.router
        self.openapi_generator = OpenAPIGenerator()
        self.swagger_ui_generator = SwaggerUIGenerator()
        self.logger = logging.getLogger(__name__)

        # Add documentation routes
        self._add_documentation_routes()

    def _add_documentation_routes(self) -> None:
        """Add OpenAPI documentation endpoints to the FastAPI router"""

        @self.fastapi_router.get('/openapi.json')
        async def openapi_spec(services: str = None):
            service_filter = services

            # Log OpenAPI request details
            self.logger.info(f"OpenAPI request: GET /openapi.json (filter: {service_filter})")

            # Use the router directly - no need for get_instance() crap
            if self.router:
                self.logger.info(f"📋 Found {len(self.router.registered_services)} registered services:")
                for service_name in self.router.registered_services.keys():
                    self.logger.info(f"   - {service_name}")

                result = await self.openapi_generator.generate_openapi_spec(
                    self.router.registered_services,
                    service_filter
                )
                self.logger.info(f"✅ Generated OpenAPI spec with {len(result.get('paths', {}))} paths")
                return result
            return {"error": "No services registered"}

        @self.fastapi_router.get('/docs')
        async def swagger_ui(services: str = None):
            """Return Swagger UI HTML page"""
            current_filter = services

            return await self.swagger_ui_generator.generate_swagger_ui(current_filter)

    async def generate_openapi_spec(self, registered_services: dict[str, Any], service_filter: str = None) -> dict[str, Any]:
        """Generate OpenAPI specification for external use"""
        return await self.openapi_generator.generate_openapi_spec(registered_services, service_filter)
