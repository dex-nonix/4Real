from typing import Any, Dict, List, Callable
from sqlalchemy import or_, func as sa_func


class CrudSwaggerGenerator:
    """Generates Swagger documentation for CRUD services."""

    def __init__(self, service):
        """Initialize with a reference to the service instance."""
        self.service = service

    def method_to_swagger(self, method: Callable) -> Dict[str, Any]:
        """ONLY CRUD service overrides this - adds dynamic model schemas."""
        
        # Get base method info from BaseApiService
        method_info = self.service.__class__.__bases__[0]().method_to_swagger(method)
        method_name = method.__name__
        
        # Add model-based schemas for CRUD operations
        if hasattr(self.service, 'model') and hasattr(self.service, 'config'):
            model = self.service.model
            config = self.service.config
            
            # Generate schemas based on method type
            if method_name == 'create':
                create_schema = self._build_create_schema(model, config)
                method_info['schemas'] = {
                    f"{self.service.__class__.__name__}Create": create_schema
                }
                
                # Override request body with model schema
                method_info['operation']["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Create"}
                        }
                    }
                }
                
            elif method_name in ['read_one', 'list_all', 'search', 'selector']:
                response_schema = self._build_response_schema(model, config)
                method_info['schemas'] = {
                    f"{self.service.__class__.__name__}Response": response_schema
                }
                
                # Override response content with model schema
                for status_code in [200, 201]:
                    if str(status_code) in method_info['operation']["responses"]:
                        method_info['operation']["responses"][str(status_code)]["content"] = {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Response"}
                            }
                        }
            
            elif method_name == 'update':
                # Add update and response schemas
                update_schema = self._build_update_schema(model, config)
                response_schema = self._build_response_schema(model, config)
                method_info['schemas'] = {
                    f"{self.service.__class__.__name__}Update": update_schema,
                    f"{self.service.__class__.__name__}Response": response_schema
                }
                
                # Override request body with model schema
                method_info['operation']["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Update"}
                        }
                    }
                }
                
                # Override response content with model schema
                for status_code in [200, 201]:
                    if str(status_code) in method_info['operation']["responses"]:
                        method_info['operation']["responses"][str(status_code)]["content"] = {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Response"}
                            }
                        }
        
        return method_info

    def _generate_model_schemas(self) -> Dict[str, Any]:
        """Generate OpenAPI schemas from service.model + service.config."""
        if not hasattr(self.service, 'model'):
            return {}
            
        model = self.service.model
        config = self.service.config
        
        # Create schemas for different operations
        schemas = {}
        
        # Create schema
        create_schema = self._build_create_schema(model, config)
        if create_schema:
            schemas[f"{self.service.__class__.__name__}Create"] = create_schema
        
        # Update schema
        update_schema = self._build_update_schema(model, config)
        if update_schema:
            schemas[f"{self.service.__class__.__name__}Update"] = update_schema
        
        # Response schema
        response_schema = self._build_response_schema(model, config)
        if response_schema:
            schemas[f"{self.service.__class__.__name__}Response"] = response_schema
        
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
            
            # Provide sensible defaults for missing decorator info (like BaseApiService does)
            if not summary:
                summary = f"{method_name.replace('_', ' ').title()}"
            if not description:
                description = f"Endpoint for {method_name.replace('_', ' ')}"
            if not tags:
                # Generate proper, readable tag names from service class
                service_name = self.service.__class__.__name__.replace('Service', '')
                # Split camelCase into words and capitalize properly
                import re
                words = re.findall(r'[A-Z][a-z]*|[A-Z]+(?=[A-Z][a-z]|$)', service_name)
                if words:
                    # Handle special cases for better readability
                    if len(words) == 1:
                        tag = words[0]
                    elif words[0] == 'AI' and len(words) > 1:
                        tag = 'AI ' + ' '.join(words[1:])
                    elif words[0] == 'MCP' and len(words) > 1:
                        tag = 'MCP ' + ' '.join(words[1:])
                    else:
                        tag = ' '.join(words)
                else:
                    tag = service_name
                tags = [tag]
            if not status_codes:
                status_codes = {200: 'Success', 400: 'Bad Request', 500: 'Internal Server Error'}
            
            # Determine request/response schemas based on method
            request_schema = None
            response_schema = None
            
            if method_name == 'create':
                request_schema = {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Create"}
                response_schema = {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Response"}
            elif method_name in ['read_one', 'list_all', 'search', 'selector']:
                response_schema = {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Response"}
            elif method_name == 'update':
                request_schema = {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Update"}
                response_schema = {"$ref": f"#/components/schemas/{self.service.__class__.__name__}Response"}
            
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

    def generate_swagger(self, service_name: str) -> Dict[str, Any]:
        """Generate complete Swagger documentation for CRUD operations."""
        
        # Get exposed methods from the service instance
        exposed_methods = self.service.get_exposed_methods()
        
        # Generate paths from exposed methods
        raw_paths = self._generate_crud_paths(exposed_methods)
        
        # Add service prefix to ALL paths (service_name is permanent, no fallback)
        paths = {}
        for raw_path, path_info in raw_paths.items():
            full_path = f"/{service_name}{raw_path}" if not raw_path.startswith(f"/{service_name}") else raw_path
            paths[full_path] = path_info
        
        # Generate schemas from model
        schemas = self._generate_model_schemas()
        
        return {
            'schemas': schemas,
            'paths': paths,
            'tags': [service_name.title()]  # Tags come from service_name, not class name
        } 