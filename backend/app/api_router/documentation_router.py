from __future__ import annotations

from flask import Blueprint, jsonify
from typing import Any

from .openapi_generator import OpenAPIGenerator
from .swagger_ui_generator import SwaggerUIGenerator

class DocumentationRouter:
    """Handles documentation-related routes and endpoints."""

    def __init__(self, blueprint: Blueprint) -> None:
        self.blueprint = blueprint
        self.openapi_generator = OpenAPIGenerator()
        self.swagger_ui_generator = SwaggerUIGenerator()
        
        # Add documentation routes
        self._add_documentation_routes()

    def _add_documentation_routes(self) -> None:
        """Add OpenAPI documentation endpoints to the blueprint"""
        
        @self.blueprint.route('/openapi.json')
        def openapi_spec():
            """Return OpenAPI 3.0 specification as JSON"""
            # We need to get the registered services from the main router
            # This will be set by the main APIRouter
            from .api_router import APIRouter
            router = APIRouter.get_instance()
            if router:
                return jsonify(self.openapi_generator.generate_openapi_spec(router.registered_services))
            return jsonify({"error": "No services registered"}), 500
        
        @self.blueprint.route('/docs')
        def swagger_ui():
            """Return Swagger UI HTML page"""
            return self.swagger_ui_generator.generate_swagger_ui()

    def generate_openapi_spec(self, registered_services: dict[str, Any]) -> dict[str, Any]:
        """Generate OpenAPI specification for external use"""
        return self.openapi_generator.generate_openapi_spec(registered_services)
