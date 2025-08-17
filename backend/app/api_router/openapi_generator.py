from __future__ import annotations

from typing import Any, Callable, Dict, List
import re

class OpenAPIGenerator:
    """Handles OpenAPI 3.0 specification generation from registered services."""

    def __init__(self) -> None:
        pass

    def generate_openapi_spec(self, registered_services: Dict[str, Any], service_filter: str = None) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification from registered services
        
        Args:
            registered_services: Dictionary of registered services
            service_filter: Comma-separated service names to include (e.g., "chat,artists")
        """
        
        paths = {}
        components = {"schemas": {}}
        tags = []
        
        # Parse service filter if provided
        allowed_services = None
        if service_filter:
            allowed_services = [s.strip().lower() for s in service_filter.split(',')]
            print(f"🎯 Filtering services: {allowed_services}")
        
        # Process each registered service
        for service_name, service in registered_services.items():
            # Skip services not in filter if filter is specified
            if allowed_services and service_name.lower() not in allowed_services:
                print(f"⏭️  Skipping service '{service_name}' (not in filter)")
                continue
            print(f"✅ Processing service '{service_name}'")
            
            # Get service's Swagger definitions via to_swagger() method
            if hasattr(service, 'to_swagger'):
                service_swagger = service.to_swagger()
                
                # Add schemas to components
                if 'schemas' in service_swagger:
                    components["schemas"].update(service_swagger['schemas'])
                
                # Add tags
                if 'tags' in service_swagger:
                    tags.extend(service_swagger['tags'])
                
                # Add paths from service
                if 'paths' in service_swagger:
                    paths.update(service_swagger['paths'])
            
            # Process exposed methods for additional paths (fallback for services without to_swagger)
            for attr_name in dir(service):
                method = getattr(service, attr_name)
                if hasattr(method, '_exposed'):
                    # Only generate paths if service doesn't provide them via to_swagger
                    if not hasattr(service, 'to_swagger') or 'paths' not in service.to_swagger():
                        path_info = self._generate_path_info(service_name, method)
                        paths.update(path_info)
                    
                    # Add DTO schemas to components (backward compatibility)
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

    def _normalize_path(self, service_name: str, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        # Convert `{id}` style placeholders to Flask `<id>`
        flask_path = path.replace('{', '<').replace('}', '>')
        return f'/{service_name}{flask_path}'
