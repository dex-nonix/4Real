# AI_README: Nonix Template System API

## Requirements
- Python 3.8+
- nonix_plugin
- nonix_di
- nonix_web_db
- jinja2
- jinja2-async-environment

## Core Classes & Interfaces

### Main Plugin
```python
class NxWebTemplatePlugin(BasePlugin):
    """Template management plugin with database and filesystem support"""
    def __init__(self, config: Dict[str, Any]) -> None
    def _configure(self, config: Dict[str, Any]) -> None: """Configure renderer with search paths"""
    # Public attributes
    template_service: TemplateService
    template_renderer: TemplateRenderer
```

### Template Service
```python
class TemplateService(BaseCrudService):
    """Service for template CRUD operations and rendering"""
    def __init__(self) -> None
    def configure_renderer(self, search_paths: List[str] = None) -> None: """Initialize renderer with search paths"""
    def add_search_path(self, path: str) -> None: """Add filesystem path for template search"""
    def remove_search_path(self, path: str) -> None: """Remove filesystem path from search"""
    def list_search_paths(self) -> List[str]: """List all registered search paths"""
    def clear_search_paths(self) -> None: """Clear all search paths"""
    async def render_template(self, template_name: str, context: Dict[str, Any] = None) -> str: """Render template by name"""
    async def render_template_by_id(self, template_id: int, context: Dict[str, Any] = None) -> str: """Render template by ID"""
    async def get_template_content(self, template_name: str) -> str: """Get raw template content"""
    async def list_available_templates(self) -> Dict[str, Dict[str, Any]]: """List all templates with metadata"""
    def clear_template_cache(self) -> None: """Clear template cache"""
    # Public attributes
    template_renderer: TemplateRenderer
```

### Template Renderer
```python
class TemplateRenderer:
    """Core template rendering engine with Jinja2"""
    def __init__(self, search_paths: List[Path] = None) -> None
    async def render_by_name(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> str: """Render template by name"""
    async def render_by_id(self, template_id: int, context: Optional[Dict[str, Any]] = None) -> str: """Render template by ID"""
    async def render_template_object(self, template, context: Optional[Dict[str, Any]] = None) -> str: """Render Template model instance"""
    async def get_template_content(self, template_name: str) -> str: """Get raw template content"""
    async def list_available_templates(self) -> Dict[str, Dict[str, Any]]: """List all templates with metadata"""
    async def _get_template_by_name(self, template_name: str) -> Template: """Get template model by name"""
    async def _get_template_by_id(self, template_id: int) -> Template: """Get template model by ID"""
    async def _render_template(self, template, context: Optional[Dict[str, Any]] = None) -> str: """Render template object"""
    def clear_cache(self) -> None: """Clear Jinja2 template cache"""
    # Public attributes
    loader: DatabaseTemplateLoader
    env: AsyncEnvironment
```

### Database Template Loader
```python
class DatabaseTemplateLoader:
    """Custom Jinja2 loader combining database and filesystem templates"""
    def __init__(self, search_paths: List[Path] = None) -> None
    async def get_source(self, environment, template) -> tuple: """Get template source from database or filesystem"""
    def list_templates(self) -> List[str]: """List all available template names"""
    def update_search_paths(self, search_paths: List[Path]) -> None: """Update filesystem search paths"""
    # Public attributes
    search_paths: List[Path]
```

### Template Model
```python
class Template:
    """Database model for templates"""
    # Public attributes
    id: int
    name: str
    content: str
    description: Optional[str]
    parent_template_id: Optional[int]
    parent_template: Optional[Template]
    created_at: datetime
    updated_at: datetime
```

### Template Router
```python
class TemplateRouter(NxWebServerCrudRouter):
    """Web API router for template CRUD operations"""
    # Public attributes
    service: TemplateService
```

## Integration Points
```python
# Inject services in other plugins
from nonix_di import NxInject

class MyPlugin(BasePlugin):
    template_service: TemplateService = NxInject(TemplateService)
    template_renderer: TemplateRenderer = NxInject(TemplateRenderer)

    async def render_content(self, template_name: str, data: dict) -> str:
        return await self.template_service.render_template(template_name, data)

# Configure search paths
template_service.configure_renderer([
    "./templates",
    "/opt/myapp/templates"
])

# Add/remove search paths dynamically
template_service.add_search_path("./custom_templates")
template_service.remove_search_path("./old_templates")

# Enable template plugin
settings.PLUGINS = [
    {"name": "web_db"},    # Required for database
    {"name": "template"}   # Template plugin
]

# Template rendering examples
rendered = await template_service.render_template("welcome.html", {"name": "User"})
content = await template_service.get_template_content("email.txt")
templates = await template_service.list_available_templates()
```

## Configuration Schema
```json
{
  "name": "template",
  "version": "1.0.0",
  "class": "NxWebTemplatePlugin",
  "dependencies": ["web_db"],
  "config": {
    "template_search_paths": [
      "./templates",
      "/opt/myapp/templates"
    ]
  }
}
```
