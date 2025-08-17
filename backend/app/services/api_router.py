from __future__ import annotations

from flask import Blueprint, request, current_app, jsonify
from functools import wraps
from typing import Any, Callable, Dict, List
import logging
import traceback
import sys
import re

class APIRouter:
    """Blueprint that auto-registers all services and generates OpenAPI documentation."""

    def __init__(self) -> None:
        self.blueprint = Blueprint('api', __name__)
        self.registered_services: dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Add OpenAPI documentation routes
        self._add_documentation_routes()

    def _add_documentation_routes(self) -> None:
        """Add OpenAPI documentation endpoints to the blueprint"""
        
        @self.blueprint.route('/openapi.json')
        def openapi_spec():
            """Return OpenAPI 3.0 specification as JSON"""
            return jsonify(self.generate_openapi_spec())
        
        @self.blueprint.route('/docs')
        def swagger_ui():
            """Return Swagger UI HTML page"""
            return self._generate_swagger_ui()

    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification from registered services"""
        
        paths = {}
        components = {"schemas": {}}
        tags = []
        
        # Process each registered service
        for service_name, service in self.registered_services.items():
            for attr_name in dir(service):
                method = getattr(service, attr_name)
                if hasattr(method, '_exposed'):
                    path_info = self._generate_path_info(service_name, method)
                    paths.update(path_info)
                    
                    # Add DTO schemas to components
                    if hasattr(method, '_request_dto') and method._request_dto:
                        schema_name = method._request_dto.__name__
                        components["schemas"][schema_name] = method._request_dto.model_json_schema()
                    
                    if hasattr(method, '_response_dto') and method._response_dto:
                        schema_name = method._response_dto.__name__
                        components["schemas"][schema_name] = method._response_dto.model_json_schema()
                    
                    # Collect PROCESSED tags (not original tags)
                    if hasattr(method, '_tags'):
                        raw_tags = method._tags
                        if raw_tags and len(raw_tags) > 0:
                            processed_tags = []
                            for tag in raw_tags:
                                if isinstance(tag, str):
                                    # Replace __SERVICE_NAME__ marker with actual service name
                                    if tag == "__SERVICE_NAME__":
                                        processed_tag = service_name.title()
                                    else:
                                        processed_tag = tag.replace('{service_name}', service_name.title())
                                    processed_tags.append(processed_tag)
                                else:
                                    processed_tags.append(tag)
                            tags.extend(processed_tags)
                        else:
                            # If no tags provided, use service name as default
                            tags.append(service_name.title())
                    else:
                        # If no _tags attribute, use service name as default
                        tags.append(service_name.title())
        
        # Remove duplicate tags and sort them alphabetically
        unique_tags = [{"name": tag} for tag in sorted(set(tags))]
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Music Metadata API",
                "version": "1.0.0",
                "description": "API for managing music metadata, artists, albums, and AI analysis"
            },
            "servers": [
                {"url": "/api", "description": "API Base URL"}
            ],
            "paths": paths,
            "components": components,
            "tags": unique_tags
        }

    def _generate_path_info(self, service_name: str, method: Callable) -> Dict[str, Any]:
        """Generate OpenAPI path information for a single method"""
        
        full_path = self._normalize_path(service_name, getattr(method, '_path'))
        methods = getattr(method, '_methods', ['GET'])
        
        path_info = {}
        
        for http_method in methods:
            method_lower = http_method.lower()
            
            # Get OpenAPI metadata
            raw_summary = getattr(method, '_summary', f"{http_method} {service_name}")
            raw_description = getattr(method, '_description', f"Execute {method.__name__} on {service_name}")
            raw_tags = getattr(method, '_tags', None)
            request_dto = getattr(method, '_request_dto', None)
            response_dto = getattr(method, '_response_dto', None)
            status_codes = getattr(method, '_status_codes', {200: 'Success'})
            
            # Process dynamic fields - replace {service_name} with actual service name
            summary = raw_summary.replace('{service_name}', service_name.title()) if isinstance(raw_summary, str) else raw_summary
            description = raw_description.replace('{service_name}', service_name.title()) if isinstance(raw_description, str) else raw_description
            
            # Handle tags - if no tags provided, use service name as default
            if raw_tags is None or len(raw_tags) == 0:
                processed_tags = [service_name.title()]
            else:
                processed_tags = []
                for tag in raw_tags:
                    if isinstance(tag, str):
                        # Replace __SERVICE_NAME__ marker with actual service name
                        if tag == "__SERVICE_NAME__":
                            processed_tag = service_name.title()
                        else:
                            processed_tag = tag.replace('{service_name}', service_name.title())
                        processed_tags.append(processed_tag)
                    else:
                        processed_tags.append(tag)
            
            # Build operation object
            operation = {
                "tags": processed_tags,
                "summary": summary,
                "description": description,
                "responses": {}
            }
            
            # Add request body if POST/PUT/PATCH
            if method_lower in ['post', 'put', 'patch'] and request_dto:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{request_dto.__name__}"}
                        }
                    }
                }
            
            # Add responses
            for status_code, description_text in status_codes.items():
                response_obj = {"description": description_text}
                
                # Add response schema if available
                if response_dto and status_code in [200, 201]:
                    response_obj["content"] = {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{response_dto.__name__}"}
                        }
                    }
                
                operation["responses"][str(status_code)] = response_obj
            
            # Add path parameters if they exist
            if '{' in full_path:
                operation["parameters"] = self._extract_path_parameters(full_path)
            
            path_info[full_path] = {method_lower: operation}
        
        return path_info

    def _extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """Extract path parameters from Flask-style path"""
        parameters = []
        # Find all <param> placeholders
        matches = re.findall(r'<([^>]+)>', path)
        
        for param in matches:
            # Handle type hints like <int:id>
            if ':' in param:
                param_type, param_name = param.split(':', 1)
                # Map Flask types to OpenAPI types
                openapi_type = {
                    'int': 'integer',
                    'float': 'number',
                    'string': 'string',
                    'path': 'string'
                }.get(param_type, 'string')
            else:
                param_name = param
                openapi_type = 'string'
            
            parameters.append({
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": openapi_type}
            })
        
        return parameters

    def _generate_swagger_ui(self) -> str:
        """Generate Swagger UI HTML page"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Music Metadata API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{ margin:0; background: #fafafa; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>
        """

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

