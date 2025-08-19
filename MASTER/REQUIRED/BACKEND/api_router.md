# 🚀 APIRouter - Generic Service Router

## 🎯 **PURPOSE:**
**Generic router that auto-registers any service with exposed methods - no fancy inventions, just clean routing**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Decorators** mark exposed service methods
- **APIRouter** auto-creates Flask routes
- **Blueprint** gets registered to Flask app
- **Generic** - works with ANY service class
- **Flexible instantiation** - supports services with dependencies

## 🔧 **IMPLEMENTATION:**

### **1. Simple Decorator System:**
```python
# decorators.py
def expose(path, methods=None):
    """Simple decorator to expose service method as API route"""
    if methods is None:
        methods = ['GET']  # Default to GET
    
    def decorator(func):
        func._exposed = True
        func._path = path
        func._methods = methods
        return func
    return decorator
```

### **2. APIRouter Blueprint (services expose RELATIVE paths):**
```python
# api_router/api_router.py
from flask import Blueprint

class APIRouter:
    """Blueprint that auto-registers all services"""
    
    def __init__(self):
        self.blueprint = Blueprint('api', __name__)
        self.registered_services = {}
    
    def register_service(self, service_name, service_class, *args, **kwargs):
        """Register service with instantiation arguments and create routes from decorators"""
        service = service_class(*args, **kwargs)  # ✅ Support instantiation arguments
        self.registered_services[service_name] = service
        
        # Find all exposed methods and create routes
        for method_name in dir(service):
            method = getattr(service, method_name)
            if hasattr(method, '_exposed'):
                self._create_route(service, method, service_name)
    
    def register_service_factory(self, service_name, service_factory):
        """Register service using factory function for complex instantiation"""
        service = service_factory()
        self.registered_services[service_name] = service
        
        # Find all exposed methods and create routes
        for method_name in dir(service):
            method = getattr(service, method_name)
            if hasattr(method, '_exposed'):
                self._create_route(service, method, service_name)
    
    def _create_route(self, service, method, service_name):
        """Create Flask route from decorator info"""
        # Service methods must expose RELATIVE paths like '/', '/{id}', '/search'
        # Placeholders use `{id}` style and are normalized to `<id>` for Flask
        path = method._path
        if not path.startswith('/'):
            path = '/' + path
        flask_path = path.replace('{', '<').replace('}', '>')
        full_path = f"/{service_name}{flask_path}"
        
        @self.blueprint.route(full_path, methods=method._methods)
        def route_handler(*args, **kwargs):
            return method(service, *args, **kwargs)
    
    def list_services(self):
        """List all registered services"""
        return list(self.registered_services.keys())
    
    def get_service(self, service_name):
        """Get a specific service by name"""
        return self.registered_services.get(service_name)
```

Note:
- Services may be instantiated without arguments if they define class attributes like `model` and `config` on the subclass. The parent requires a `config` to exist (either passed or on the subclass) and will only fill missing keys from defaults; it does not create a generic config when absent.

### **3. Flask App Integration:**
```python
# app.py
from flask import Flask
from app.api_router.api_router import APIRouter
from services.artist_service import ArtistService
from services.album_service import AlbumService
 

app = Flask(__name__)
api_router = APIRouter()

# Register services (simple per-table services + ChatService)
api_router.register_service('artists', ArtistService)
api_router.register_service('albums', AlbumService)
api_router.register_service('chat', ChatService)
api_router.register_service('file-categories', FileCategoryService)
api_router.register_service('files', FileService)
api_router.register_service('file-links', FileLinkService)

# (example for complex service using factory intentionally omitted)

# Register APIRouter blueprint to /api
app.register_blueprint(api_router.blueprint, url_prefix='/api')

# DONE! Routes are auto-created from service decorators
```

## 📁 **FILE STRUCTURE:**

```
backend/
├── app/
│   ├── __init__.py
│   ├── api_router/
│   │   ├── __init__.py
│   │   ├── api_router.py        # APIRouter blueprint ONLY
│   │   ├── documentation_router.py
│   │   ├── openapi_generator.py
│   │   ├── swagger_ui_generator.py
│   │   └── compact_api_generator.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_api_service.py  # Base class with WebSocket support
│   │   ├── crud_service.py      # Generic CRUD service
│   │   ├── artist_service.py    # Artist service
│   │   └── album_service.py     # Album service
│   └── decorators.py            # @expose and @expose_ws decorators
├── config.py                     # Configuration
└── requirements.txt              # Dependencies
```

## 🎯 **KEY FEATURES:**

### **✅ Generic Router:**
- **Works with ANY service** - not tied to specific implementations
- **Auto-discovers** exposed methods via decorators
- **Creates Flask routes** automatically
- **Blueprint** gets registered to Flask app
- **Flexible instantiation** - supports services with dependencies

### **✅ Simple Decorator System:**
- **`@expose('/artists')`** - GET route, default method
- **`@expose('/artists', methods=['POST'])`** - POST route
- **`@expose('/artists/{id}')`** - route with variables
- **No complex configuration** - just path and optional methods

### **✅ Clean Architecture:**
- **Decorators** mark exposed methods
- **APIRouter** creates routes
- **Flask app** just registers blueprint
- **Services** handle business logic
- **Dependency injection** - services get what they need

## 🔄 **WORKFLOW:**

### **1. Service Uses Decorators:**
```python
class ArtistService:
    def __init__(self, db, config):
        self.db = db
        self.config = config
    
    @expose('/artists')
    def get_all(self, request):
        # Implementation here
        pass
```

### **2. Register Service with Dependencies:**
```python
api_router.register_service('artists', ArtistService, db=db, config=config)
```

### **3. Auto-Create Routes:**
- **APIRouter** finds `@expose` decorators
- **Flask routes** are created automatically
- **Blueprint** contains all routes

### **4. Register Blueprint:**
```python
app.register_blueprint(api_router.blueprint, url_prefix='/api')
```

## 📋 **USAGE EXAMPLES:**

### **1. Simple Service (No Dependencies):**
```python
class HealthService:
    @expose('/health')
    def check_health(self, request):
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @expose('/ping')
    def ping(self, request):
        return {"message": "pong"}
```

### **2. Basic Service with Dependencies (relative paths in decorators):**
```python
class AlbumService:
    def __init__(self, db, storage_path):
        self.db = db
        self.storage_path = storage_path
    
    @expose('/')
    def get_all(self, request):
        return self.db.query(Album).all()
    
    @expose('/{id}')
    def get_by_id(self, request, id):
        return self.db.query(Album).filter_by(id=id).first()
    
    @expose('/', methods=['POST'])
    def create(self, request):
        data = request.get_json()
        album = Album(**data)
        self.db.add(album)
        self.db.commit()
        return album
```

### **3. Complex Service with Multiple Dependencies:**
```python
# Example intentionally removed
```

### **4. Service Registration Examples:**
```python
# Simple service (no dependencies)
api_router.register_service('health', HealthService)

# Service with dependencies
api_router.register_service('artists', ArtistService)
api_router.register_service('personas', PersonaService)
api_router.register_service('internal-tools', InternalToolService)
api_router.register_service('persona-tool-access', PersonaToolAccessService)
api_router.register_service('mcp-servers', MCPServerService)
api_router.register_service('persona-mcp-servers', PersonaMCPServerService)
api_router.register_service('chat-sessions', ChatSessionService)
api_router.register_service('chat-messages', ChatMessageService)
api_router.register_service('tool-invocation-logs', ToolInvocationLogService)
api_router.register_service('chat', ChatService)

# Service with complex instantiation using factory (example intentionally removed)
```

## 🎯 **BENEFITS:**

### **✅ Generic and Clean:**
- **Works with ANY service** - not tied to specific patterns
- **Auto-routing** - no manual route creation
- **Blueprint** - clean Flask integration
- **Decorators** - simple method exposure
- **Dependency injection** - services get context they need

### **✅ No Over-Engineering:**
- **No complex registries**
- **No factory patterns**
- **No abstract base classes**
- **Just working, simple routing**
- **Flexible instantiation** when needed

### **✅ Easy to Extend:**
- **Add new services** - just create class with decorators
- **Add new methods** - just add `@expose` decorator
- **Custom logic** - implement whatever you want in services
- **No breaking changes** - decorators are optional
- **Handle dependencies** - pass what services need

**This APIRouter is ONLY about generic routing - the services handle their own logic and get the dependencies they need!**