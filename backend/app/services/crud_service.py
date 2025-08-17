from __future__ import annotations
import logging


from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, date
from flask import jsonify, Request
from sqlalchemy import or_, func as sa_func

from .. import db
from ..decorators import expose
from .base_api_service import BaseApiService

# Set up logging
logger = logging.getLogger(__name__)


class CrudService(BaseApiService):
    """Generic CRUD service that handles ALL operations automatically using config."""

    def __init__(self, model_class: Any | None = None, config: Optional[Dict[str, Any]] = None) -> None:
        # Model resolution: explicit arg wins; else existing attribute; else error
        if model_class is not None:
            self.model = model_class
        elif not hasattr(self, 'model'):
            raise ValueError('model is required')

        # Config resolution: explicit arg wins; else existing attribute; else error
        if config is not None:
            self.config = config
        elif not hasattr(self, 'config'):
            raise ValueError('config is required')

        # Apply default values for any missing config keys (no generic fallback when entirely missing)
        self.config = self._apply_default_config_values(self.config)

    def _get_default_config(self):
        """Default CRUD configuration"""
        return {
            'operations': {
                'create': True,      # Enable POST /
                'read': True,        # Enable GET / and GET /{id}
                'update': True,      # Enable PUT /{id}
                'delete': True,      # Enable DELETE /{id}
                'list': True,        # Enable GET / (list all)
                'search': True,      # Enable GET /search
                'bulk': True,        # Enable POST /bulk
                'selector': True     # Enable GET /selector and /selector/{id} (optimized for dropdowns)
            },
            'filters': {
                'enabled': True,     # Enable filtering
                'fields': [],        # Fields that can be filtered
                'operators': ['eq', 'ne', 'gt', 'lt', 'like', 'in']
            },
            'pagination': {
                'enabled': True,     # Enable pagination
                'default_page_size': 20,
                'max_page_size': 100
            },
            'sorting': {
                'enabled': True,     # Enable sorting
                'default_sort': 'id',
                'allowed_fields': []
            },
            'validation': {
                'enabled': True,     # Enable validation
                'required_fields': [],
                'unique_fields': []
            },
            'selector': {
                'enabled': True,     # Enable selector optimization
                'fields': ['name'],  # Extra fields to return. NOTE: 'id' is ALWAYS included automatically
                'display_format': None,    # Custom display format (e.g., 'firstName + " " + lastName')
                'search_fields': ['name'], # Fields to search in for selector
                'limit': 100,              # Max items for selector (performance)
                'order_by': 'name'         # How to order selector items
            }
        }

    def _apply_default_config_values(self, provided_config):
        """Fill only missing keys from defaults; do not create a config when absent."""
        defaults = self._get_default_config()

        def merge(dst, src_defaults):
            for key, def_value in src_defaults.items():
                if key not in dst:
                    dst[key] = def_value
                else:
                    cur_value = dst[key]
                    if isinstance(cur_value, dict) and isinstance(def_value, dict):
                        dst[key] = merge(cur_value, def_value)
            return dst

        return merge(dict(provided_config), defaults)

    def to_swagger(self) -> Dict[str, Any]:
        """Generate Swagger documentation for CRUD operations from model + config."""
        
        # Get exposed methods info
        exposed_methods = self.get_exposed_methods()
        
        # Generate schemas from model
        schemas = self._generate_model_schemas()
        
        # Generate paths from exposed methods
        paths = self._generate_crud_paths(exposed_methods)
        
        return {
            'schemas': schemas,
            'paths': paths,
            'tags': [self.__class__.__name__.replace('Service', '').title()]
        }
    
    def _generate_model_schemas(self) -> Dict[str, Any]:
        """Generate OpenAPI schemas from service.model + service.config."""
        if not hasattr(self, 'model'):
            return {}
            
        model = self.model
        config = self.config
        
        # Create schemas for different operations
        schemas = {}
        
        # Create schema
        create_schema = self._build_create_schema(model, config)
        if create_schema:
            schemas[f"{self.__class__.__name__}Create"] = create_schema
        
        # Update schema
        update_schema = self._build_update_schema(model, config)
        if update_schema:
            schemas[f"{self.__class__.__name__}Update"] = update_schema
        
        # Response schema
        response_schema = self._build_response_schema(model, config)
        if response_schema:
            schemas[f"{self.__class__.__name__}Response"] = response_schema
        
        return schemas
    
    def _build_create_schema(self, model: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build schema for create operations."""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        required_fields = config.get('validation', {}).get('required_fields', [])
        
        for column in model.__table__.columns:
            # Skip ID and timestamps for create
            if column.name in ['id', 'created_at', 'updated_at']:
                continue
                
            # Add field to schema
            field_schema = self._column_to_openapi_schema(column)
            schema["properties"][column.name] = field_schema
            
            # Mark as required if in config
            if column.name in required_fields:
                schema["required"].append(column.name)
        
        return schema
    
    def _build_update_schema(self, model: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build schema for update operations."""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # All fields are optional for updates
        for column in model.__table__.columns:
            # Skip ID and timestamps for update
            if column.name in ['id', 'created_at', 'updated_at']:
                continue
                
            # Add field to schema
            field_schema = self._column_to_openapi_schema(column)
            schema["properties"][column.name] = field_schema
        
        return schema
    
    def _build_response_schema(self, model: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build schema for response operations."""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        required_fields = config.get('validation', {}).get('required_fields', [])
        
        for column in model.__table__.columns:
            # Add field to schema
            field_schema = self._column_to_openapi_schema(column)
            schema["properties"][column.name] = field_schema
            
            # Mark as required if in config or if it's a core field
            if column.name in required_fields or column.name in ['id', 'created_at', 'updated_at']:
                schema["required"].append(column.name)
        
        return schema
    
    def _column_to_openapi_schema(self, column: Any) -> Dict[str, Any]:
        """Convert SQLAlchemy column to OpenAPI schema."""
        # Map SQLAlchemy types to OpenAPI types
        type_mapping = {
            'String': 'string',
            'Text': 'string',
            'Integer': 'integer',
            'BigInteger': 'integer',
            'Float': 'number',
            'Numeric': 'number',
            'Boolean': 'boolean',
            'Date': 'string',
            'DateTime': 'string',
            'Time': 'string',
            'JSON': 'object'
        }
        
        column_type = type(column.type).__name__
        openapi_type = type_mapping.get(column_type, 'string')
        
        schema = {"type": openapi_type}
        
        # Add format for date/time
        if column_type in ['Date', 'DateTime', 'Time']:
            schema["format"] = column_type.lower()
        
        # Add length constraints
        if hasattr(column.type, 'length'):
            schema["maxLength"] = column.type.length
        
        # Add description
        schema["description"] = f"{column.name} field"
        
        return schema
    
    def _generate_crud_paths(self, exposed_methods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate OpenAPI paths from exposed methods."""
        paths = {}
        
        for method_info in exposed_methods:
            method_name = method_info['name']
            path = method_info['path']
            methods = method_info['methods']
            summary = method_info['summary']
            description = method_info['description']
            tags = method_info['tags']
            status_codes = method_info['status_codes']
            
            # Determine request/response schemas based on method
            request_schema = None
            response_schema = None
            
            if method_name == 'create':
                request_schema = {"$ref": f"#/components/schemas/{self.__class__.__name__}Create"}
                response_schema = {"$ref": f"#/components/schemas/{self.__class__.__name__}Response"}
            elif method_name in ['read_one', 'list_all', 'search', 'selector']:
                response_schema = {"$ref": f"#/components/schemas/{self.__class__.__name__}Response"}
            elif method_name == 'update':
                request_schema = {"$ref": f"#/components/schemas/{self.__class__.__name__}Update"}
                response_schema = {"$ref": f"#/components/schemas/{self.__class__.__name__}Response"}
            
            # Build operation object
            operation = {
                "tags": tags,
                "summary": summary,
                "description": description,
                "responses": {}
            }
            
            # Add request body if POST/PUT/PATCH
            if any(m in ['POST', 'PUT', 'PATCH'] for m in methods) and request_schema:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": request_schema
                        }
                    }
                }
            
            # Add responses
            for status_code, description_text in status_codes.items():
                response_obj = {"description": description_text}
                
                if response_schema and status_code in [200, 201]:
                    response_obj["content"] = {
                        "application/json": {
                            "schema": response_schema
                        }
                    }
                
                operation["responses"][str(status_code)] = response_obj
            
            # Add path parameters if they exist
            if '{' in path:
                operation["parameters"] = self._extract_path_parameters(path)
            
            # Add to paths
            for method in methods:
                method_lower = method.lower()
                if path not in paths:
                    paths[path] = {}
                paths[path][method_lower] = operation
        
        return paths
    
    def _extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """Extract path parameters from Flask-style path"""
        parameters = []
        # Find all <param> placeholders
        import re
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

    def method_to_swagger(self, method: Callable) -> Dict[str, Any]:
        """ONLY CRUD service overrides this - adds dynamic model schemas."""
        
        # Get base method info from BaseApiService
        method_info = super().method_to_swagger(method)
        method_name = method.__name__
        
        # Add model-based schemas for CRUD operations
        if hasattr(self, 'model') and hasattr(self, 'config'):
            model = self.model
            config = self.config
            
            # Generate schemas based on method type
            if method_name == 'create':
                create_schema = self._build_create_schema(model, config)
                method_info['schemas'] = {
                    f"{self.__class__.__name__}Create": create_schema
                }
                
                # Override request body with model schema
                method_info['operation']["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{self.__class__.__name__}Create"}
                        }
                    }
                }
                
            elif method_name in ['read_one', 'list_all', 'search', 'selector']:
                response_schema = self._build_response_schema(model, config)
                method_info['schemas'] = {
                    f"{self.__class__.__name__}Response": response_schema
                }
                
                # Override response content with model schema
                for status_code in [200, 201]:
                    if str(status_code) in method_info['operation']["responses"]:
                        method_info['operation']["responses"][str(status_code)]["content"] = {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{self.__class__.__name__}Response"}
                            }
                        }
            
            elif method_name == 'update':
                # Add update and response schemas
                update_schema = self._build_update_schema(model, config)
                response_schema = self._build_response_schema(model, config)
                method_info['schemas'] = {
                    f"{self.__class__.__name__}Update": update_schema,
                    f"{self.__class__.__name__}Response": response_schema
                }
                
                # Override request body with model schema
                method_info['operation']["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{self.__class__.__name__}Update"}
                        }
                    }
                }
                
                # Override response content with model schema
                for status_code in [200, 201]:
                    if str(status_code) in method_info['operation']["responses"]:
                        method_info['operation']["responses"][str(status_code)]["content"] = {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{self.__class__.__name__}Response"}
                            }
                        }
        
        return method_info

