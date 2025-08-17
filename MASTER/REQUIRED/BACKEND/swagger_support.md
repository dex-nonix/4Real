# 🚀 Swagger/OpenAPI Support with DTOs - Integration Guide

## 🎯 **WHAT THIS GUIDE DOES:**

This guide shows you how to add **automatic Swagger/OpenAPI documentation** to your existing Flask API by:
1. **Adding DTOs (Data Transfer Objects)** for clean data contracts
2. **Enhancing the @expose decorator** to capture API metadata
3. **Generating OpenAPI specifications** automatically from your code
4. **Adding Swagger UI** for interactive API documentation

## 🏗️ **ARCHITECTURE OVERVIEW:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   DTOs          │    │   Services      │
│   Models        │◄──►│   (API Layer)   │◄──►│   (@expose)     │
│   (SQLAlchemy)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   APIRouter     │
                       │   (Auto-gen)    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   OpenAPI Spec  │
                       │   + Swagger UI  │
                       └─────────────────┘
```

## 📋 **STEP-BY-STEP INTEGRATION:**

### **Step 1: Install Required Dependencies**

Add these to your `backend/requirements.txt`:

```txt
# Existing dependencies...
pydantic>=2.0.0
flask-swagger-ui>=4.11.1
```

Then install:
```bash
cd backend
pip install -r requirements.txt
```

### **Step 2: Create DTO Base Classes**

Create `backend/app/dtos/__init__.py`:

```python
# This file makes the dtos folder a Python package
```

Create `backend/app/dtos/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BaseDTO(ABC, BaseModel):
    """Abstract base class for all DTOs with common functionality"""
    
    class Config:
        from_attributes = True  # Allow ORM model conversion
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @classmethod
    @abstractmethod
    def from_model(cls, model: Any) -> 'BaseDTO':
        """Convert database model to DTO - MUST be implemented by subclasses"""
        pass
    
    @classmethod
    @abstractmethod
    def to_model_data(cls) -> Dict[str, Any]:
        """Convert DTO to model-compatible data - MUST be implemented by subclasses"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for JSON responses)"""
        return self.model_dump()

class CreateDTO(BaseDTO):
    """Base class for creation DTOs (no ID, no timestamps)"""
    pass

class UpdateDTO(BaseDTO):
    """Base class for update DTOs (partial updates, no timestamps)"""
    pass

class ResponseDTO(BaseDTO):
    """Base class for response DTOs (full data, read-only)"""
    pass

class ListResponseDTO(ResponseDTO):
    """Base class for list response DTOs (pagination, filtering)"""
    data: List[ResponseDTO]
    total: int
    page: int
    per_page: int
```

### **Step 3: Create Example DTOs**

Create `backend/app/dtos/artist_dtos.py`:

```python
from typing import Optional
from datetime import datetime
from pydantic import Field
from .base import CreateDTO, UpdateDTO, ResponseDTO, ListResponseDTO
from ..models.artist import Artist

# DTO for creating a new artist
class ArtistCreateDTO(CreateDTO):
    name: str = Field(..., min_length=1, max_length=255, description="Artist name")
    abbreviation: Optional[str] = Field(None, max_length=50, description="Artist abbreviation")
    persona: Optional[str] = Field(None, description="Artist persona description")
    birth_date: Optional[datetime] = Field(None, description="Artist birth date")

# DTO for updating an existing artist
class ArtistUpdateDTO(UpdateDTO):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    abbreviation: Optional[str] = Field(None, max_length=50)
    persona: Optional[str] = None
    birth_date: Optional[datetime] = None

# DTO for artist responses
class ArtistResponseDTO(ResponseDTO):
    id: int = Field(..., description="Artist ID")
    name: str = Field(..., description="Artist name")
    abbreviation: Optional[str] = Field(None, description="Artist abbreviation")
    persona: Optional[str] = Field(None, description="Artist persona description")
    birth_date: Optional[datetime] = Field(None, description="Artist birth date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @classmethod
    def from_model(cls, model: Artist) -> 'ArtistResponseDTO':
        """Convert Artist model to ArtistResponseDTO"""
        return cls(
            id=model.id,
            name=model.name,
            abbreviation=model.abbreviation,
            persona=model.persona,
            birth_date=model.birth_date,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def to_model_data(self) -> Dict[str, Any]:
        """Convert DTO to model-compatible data (exclude computed fields)"""
        return self.model_dump(exclude={'id', 'created_at', 'updated_at'})

# DTO for list responses
class ArtistListResponseDTO(ListResponseDTO):
    data: List[ArtistResponseDTO]
```

### **Step 4: Enhance the @expose Decorator**

Update `backend/app/decorators.py`:

```python
from typing import Callable, List, Optional, Dict, Any, type

def expose(
    path: str, 
    methods: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    request_dto: Optional[type] = None,
    response_dto: Optional[type] = None,
    status_codes: Optional[Dict[int, str]] = None
) -> Callable:
    """
    Enhanced decorator to expose service method as API route with OpenAPI metadata.
    
    Args:
        path: API path (e.g., '/{id}', '/search')
        methods: HTTP methods (default: ['GET'])
        summary: Short description for OpenAPI
        description: Detailed description for OpenAPI
        tags: API grouping tags (e.g., ['Artists'])
        request_dto: DTO class for request validation
        response_dto: DTO class for response schema
        status_codes: HTTP status codes and descriptions
    """
    if methods is None:
        methods = ['GET']
    
    def decorator(func: Callable) -> Callable:
        # Set basic route info (existing functionality)
        setattr(func, '_exposed', True)
        setattr(func, '_path', path)
        setattr(func, '_methods', methods)
        
        # Set OpenAPI metadata (new functionality)
        setattr(func, '_summary', summary)
        setattr(func, '_description', description)
        setattr(func, '_tags', tags or [])
        setattr(func, '_request_dto', request_dto)
        setattr(func, '_response_dto', response_dto)
        setattr(func, '_status_codes', status_codes or {200: 'Success'})
        
        return func
    
    return decorator
```

### **Step 5: Update APIRouter for OpenAPI Generation**

Update `backend/app/services/api_router.py`:

```python
from __future__ import annotations

from flask import Blueprint, request, current_app, jsonify
from functools import wraps
from typing import Any, Callable, Dict
import logging
import traceback
import sys

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
                    
                    # Collect tags
                    if hasattr(method, '_tags'):
                        tags.extend(method._tags)
        
        # Remove duplicate tags
        unique_tags = [{"name": tag} for tag in set(tags)]
        
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
            summary = getattr(method, '_summary', f"{http_method} {service_name}")
            description = getattr(method, '_description', f"Execute {method.__name__} on {service_name}")
            tags = getattr(method, '_tags', [service_name.title()])
            request_dto = getattr(method, '_request_dto', None)
            response_dto = getattr(method, '_response_dto', None)
            status_codes = getattr(method, '_status_codes', {200: 'Success'})
            
            # Build operation object
            operation = {
                "tags": tags,
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
        import re
        
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

    # ... existing methods remain the same ...
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
```

### **Step 6: Update a Service to Use DTOs**

Update `backend/app/services/artist_service.py`:

```python
from __future__ import annotations

from .crud_service import CrudService
from ..models.artist import Artist
from ..dtos.artist_dtos import ArtistCreateDTO, ArtistUpdateDTO, ArtistResponseDTO, ArtistListResponseDTO
from flask import request, jsonify
from .. import db

class ArtistService(CrudService):
    model = Artist
    config = {
        'filters': {
            'fields': ['name', 'abbreviation'],
        },
        'sorting': {
            'default_sort': 'name',
            'allowed_fields': ['name', 'abbreviation', 'created_at'],
        },
        'validation': {
            'required_fields': ['name'],
            'unique_fields': ['name'],
        },
        'selector': {
            'fields': ['name', 'abbreviation'],
            'display_format': 'name',
            'search_fields': ['name', 'abbreviation']
        },
    }

    # Override the create method to use DTOs
    def create(self, request: request) -> ArtistResponseDTO:
        """Create a new artist using DTO validation"""
        try:
            # Validate input using DTO
            create_dto = ArtistCreateDTO.model_validate(request.get_json())
            
            # Convert to model data
            model_data = create_dto.to_model_data()
            
            # Create and save
            artist = Artist(**model_data)
            db.session.add(artist)
            db.session.commit()
            
            # Return response DTO
            return ArtistResponseDTO.from_model(artist)
            
        except Exception as exc:
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    # Override the read_one method to use DTOs
    def read_one(self, request: request, id: int) -> ArtistResponseDTO:
        """Get artist by ID using DTO response"""
        try:
            artist = Artist.query.get_or_404(id)
            return ArtistResponseDTO.from_model(artist)
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500

    # Override the update method to use DTOs
    def update(self, request: request, id: int) -> ArtistResponseDTO:
        """Update artist using DTO validation"""
        try:
            artist = Artist.query.get_or_404(id)
            
            # Validate input using DTO
            update_dto = ArtistUpdateDTO.model_validate(request.get_json())
            
            # Convert to model data (only provided fields)
            model_data = update_dto.model_dump(exclude_unset=True)
            
            # Update fields
            for key, value in model_data.items():
                setattr(artist, key, value)
            
            db.session.commit()
            
            # Return response DTO
            return ArtistResponseDTO.from_model(artist)
            
        except Exception as exc:
            db.session.rollback()
            return jsonify({'error': str(exc)}), 500

    # Override the list_all method to use DTOs
    def list_all(self, request: request) -> ArtistListResponseDTO:
        """Get all artists using DTO response"""
        try:
            artists = Artist.query.all()
            artist_dtos = [ArtistResponseDTO.from_model(artist) for artist in artists]
            
            return ArtistListResponseDTO(
                data=artist_dtos,
                total=len(artist_dtos),
                page=1,
                per_page=len(artist_dtos)
            )
            
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500
```

### **Step 7: Test the Integration**

1. **Start your Flask app:**
```bash
cd backend
python -m flask run
```

2. **Check the OpenAPI spec:**
   - Visit: `http://localhost:5000/api/openapi.json`
   - You should see a JSON file with your API specification

3. **Check the Swagger UI:**
   - Visit: `http://localhost:5000/api/docs`
   - You should see an interactive API documentation interface

## 🎯 **WHAT YOU GET:**

### **✅ Automatic API Documentation:**
- **OpenAPI 3.0 specification** generated from your code
- **Swagger UI interface** for testing and exploring your API
- **Schema validation** for all request/response models
- **Interactive documentation** that stays in sync with your code

### **✅ Data Validation:**
- **Input validation** using Pydantic schemas
- **Type safety** throughout your API layer
- **Automatic error handling** for invalid data
- **Consistent validation rules** across all endpoints

### **✅ Clean Architecture:**
- **Separation of concerns** between models, DTOs, and services
- **Reusable DTOs** for different operations
- **Type hints** for better IDE support
- **Easy testing** with structured data objects

## 🔧 **TROUBLESHOOTING:**

### **Common Issues:**

1. **Import Errors:**
   - Make sure you created the `dtos` folder as a Python package
   - Check that all import paths are correct

2. **Pydantic Validation Errors:**
   - Ensure your DTOs match your database model structure
   - Check that required fields are properly marked

3. **Swagger UI Not Loading:**
   - Verify the `/api/openapi.json` endpoint returns valid JSON
   - Check browser console for JavaScript errors

4. **Routes Not Working:**
   - Ensure your services are properly registered with APIRouter
   - Check that `@expose` decorators are applied correctly

## 🚀 **NEXT STEPS:**

### **Phase 1: Complete DTOs for All Services**
- Create DTOs for Album, Track, Style, etc.
- Update all services to use DTOs
- Test validation and responses

### **Phase 2: Add More OpenAPI Features**
- Add authentication schemes
- Include request/response examples
- Add more detailed descriptions

### **Phase 3: Frontend Integration**
- Use generated schemas in your Vue frontend
- Add automatic form generation
- Implement client-side validation

## 🏆 **SUMMARY:**

This integration gives you:
- **Professional API documentation** that updates automatically
- **Data validation** that catches errors early
- **Clean separation** between database models and API contracts
- **Type safety** throughout your application
- **Interactive testing** via Swagger UI

The system is designed to work with your existing code - you can migrate services one at a time, and everything remains backward compatible!
