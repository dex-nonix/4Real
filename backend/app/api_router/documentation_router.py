from __future__ import annotations

from flask import Blueprint, jsonify
from typing import Any

from .openapi_generator import OpenAPIGenerator
from .swagger_ui_generator import SwaggerUIGenerator

class DocumentationRouter:
    """Handles documentation-related routes and endpoints."""

    def __init__(self, router) -> None:
        self.router = router
        self.blueprint = router.blueprint
        self.openapi_generator = OpenAPIGenerator()
        self.swagger_ui_generator = SwaggerUIGenerator()
        
        # Add documentation routes
        self._add_documentation_routes()

    def _add_documentation_routes(self) -> None:
        """Add OpenAPI documentation endpoints to the blueprint"""
        
        @self.blueprint.route('/openapi.json')
        def openapi_spec():
            """Return OpenAPI 3.0 specification as JSON"""
            from flask import request
            
            # Get service filter from query parameter
            service_filter = request.args.get('services', None)
            
            # Debug logging - MORE DETAILED
            print(f"🔍 OpenAPI request received!")
            print(f"🔍 Full request URL: {request.url}")
            print(f"🔍 Query parameters: {dict(request.args)}")
            print(f"🔍 Services filter: {service_filter}")
            print(f"🔍 Request method: {request.method}")
            
            # Use the router directly - no need for get_instance() crap
            if self.router:
                print(f"📋 Found {len(self.router.registered_services)} registered services:")
                for service_name in self.router.registered_services.keys():
                    print(f"   - {service_name}")
                
                result = self.openapi_generator.generate_openapi_spec(
                    self.router.registered_services, 
                    service_filter
                )
                print(f"✅ Generated OpenAPI spec with {len(result.get('paths', {}))} paths")
                return jsonify(result)
            return jsonify({"error": "No services registered"}), 500
        
        @self.blueprint.route('/docs')
        def swagger_ui():
            """Return Swagger UI HTML page"""
            from flask import request
            
            # Get current filter from URL query parameter
            current_filter = request.args.get('services', None)
            
            return self.swagger_ui_generator.generate_swagger_ui(current_filter)

    def generate_openapi_spec(self, registered_services: dict[str, Any], service_filter: str = None) -> dict[str, Any]:
        """Generate OpenAPI specification for external use"""
        return self.openapi_generator.generate_openapi_spec(registered_services, service_filter)
