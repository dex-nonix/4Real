from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable

class BaseApiService(ABC):
    """Base class for all API services with Swagger documentation capability."""
    
    def to_swagger(self) -> Dict[str, Any]:
        """
        Return Swagger/OpenAPI definitions for this service.
        Each service can override this to provide custom documentation.
        
        Returns:
            Dict containing OpenAPI components, paths, and schemas
        """
        # Default implementation using the working method_to_swagger
        exposed_methods = self.get_exposed_methods()
        
        paths = {}
        schemas = {}
        
        for method_info in exposed_methods:
            method = getattr(self, method_info['name'])
            swagger_info = self.method_to_swagger(method)
            
            # Add to paths and schemas
            path = swagger_info['path']
            if path not in paths:
                paths[path] = {}
            
            for method_name in swagger_info['methods']:
                paths[path][method_name.lower()] = swagger_info['operation']
            
            schemas.update(swagger_info.get('schemas', {}))
        
        return {
            'schemas': schemas,
            'paths': paths,
            'tags': []
        }
    
    def get_exposed_methods(self) -> List[Dict[str, Any]]:
        """Get all @expose methods with their metadata."""
        exposed_methods = []
        
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                method_info = {
                    'name': attr_name,
                    'path': getattr(method, '_path'),
                    'methods': getattr(method, '_methods', ['GET']),
                    'summary': getattr(method, '_summary'),
                    'description': getattr(method, '_description'),
                    'tags': getattr(method, '_tags', []),
                    'status_codes': getattr(method, '_status_codes', {}),
                    'request_schema': getattr(method, '_request_schema'),
                    'response_schema': getattr(method, '_response_schema')
                }
                exposed_methods.append(method_info)
        
        return exposed_methods
    
    def method_to_swagger(self, method: Callable) -> Dict[str, Any]:
        """DEFAULT: Convert @expose method to Swagger format. ALL subclasses use this by default."""
        
        # Extract ALL info from @expose decorator
        path = getattr(method, '_path')
        methods = getattr(method, '_methods', ['GET'])
        summary = getattr(method, '_summary')
        description = getattr(method, '_description')
        tags = getattr(method, '_tags', [])
        status_codes = getattr(method, '_status_codes', {})
        
        # 🚀 NEW: Extract schemas from decorator
        request_schema = getattr(method, '_request_schema')
        response_schema = getattr(method, '_response_schema')
        
        # Build operation object
        operation = {
            "tags": tags,
            "summary": summary,
            "description": description,
            "responses": {}
        }
        
        # 🚀 NEW: Add request body if schema provided
        if request_schema:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": request_schema
                    }
                }
            }
        
        # Add responses with schemas if provided
        for status_code, description_text in status_codes.items():
            response_obj = {"description": description_text}
            
            # 🚀 NEW: Add response schema if provided
            if response_schema and status_code in [200, 201]:
                response_obj["content"] = {
                    "application/json": {
                        "schema": response_schema
                    }
                }
            
            operation["responses"][str(status_code)] = response_obj
        
        return {
            'path': path,
            'methods': methods,
            'operation': operation,
            'tags': tags,
            'schemas': {}  # Empty by default - subclasses can override to add schemas
        }
