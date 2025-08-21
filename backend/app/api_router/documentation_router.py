from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from flask import jsonify
from flask import request

if TYPE_CHECKING:
    from .api_router import APIRouter

from .openapi_generator import OpenAPIGenerator
from .swagger_ui_generator import SwaggerUIGenerator


class DocumentationRouter:
    """Handles documentation-related routes and endpoints."""

    def __init__(self, router: 'APIRouter') -> None:
        self.router: 'APIRouter' = router
        self.blueprint = router.blueprint
        self.openapi_generator = OpenAPIGenerator()
        self.swagger_ui_generator = SwaggerUIGenerator()
        self.logger = logging.getLogger(__name__)

        # Add documentation routes
        self._add_documentation_routes()

    async def _add_documentation_routes(self) -> None:
        """Add OpenAPI documentation endpoints to the blueprint"""

        @self.blueprint.route('/openapi.json')
        async def openapi_spec():
            service_filter = request.args.get('services', None)

            # Log OpenAPI request details
            self.logger.info(f"OpenAPI request: {request.method} {request.url} (filter: {service_filter})")

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
                return jsonify(result)
            return jsonify({"error": "No services registered"}), 500

        @self.blueprint.route('/docs')
        async def swagger_ui():
            """Return Swagger UI HTML page"""
            current_filter = request.args.get('services', None)

            return await self.swagger_ui_generator.generate_swagger_ui(current_filter)

    async def generate_openapi_spec(self, registered_services: dict[str, Any], service_filter: str = None) -> dict[str, Any]:
        """Generate OpenAPI specification for external use"""
        return await self.openapi_generator.generate_openapi_spec(registered_services, service_filter)
