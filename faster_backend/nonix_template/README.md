# Nonix Template Plugin - Usage Guide

## Overview

The Nonix Template Plugin provides a comprehensive, production-ready template management and rendering system for your application. It combines database-backed template storage with filesystem-based template loading, offering powerful Jinja2 template rendering with async support, template inheritance, context management, and automatic search path resolution.

**⚠️ Important Notes**:
- This plugin serves as the template foundation for the entire Nonix ecosystem
- Provides both database-backed template storage and filesystem template loading
- Offers advanced Jinja2 rendering with async support and template inheritance
- Designed as part of the unified Nonix system where template functionality serves as a generic base for all interfaces

## Dependencies

### Core Plugin System
- **Plugin System**: For plugin lifecycle management and registration
- **Database Plugin**: For template storage and CRUD operations (`nonix_web_db`)
- **DI System**: For service injection and dependency resolution

### Template Dependencies
- **Jinja2**: For template rendering with async support
- **SQLAlchemy**: For database operations (provided by database plugin)

## Architecture

### Core Components
- **NxWebTemplatePlugin**: Main plugin that orchestrates all template functionality
- **TemplateService**: High-level service for template CRUD and rendering operations
- **TemplateRenderer**: Core rendering engine with Jinja2 integration
- **DatabaseTemplateLoader**: Custom loader that combines database and filesystem templates
- **TemplateRouter**: Web API endpoints for template management

### Data Flow
1. **Plugin loads** → Registers services and router with DI system
2. **Services initialize** → Sets up template renderer and search paths
3. **Templates load** → Database templates + filesystem templates via search paths
4. **Rendering occurs** → Jinja2 templates rendered with merged contexts
5. **API serves** → Web endpoints provide template management and rendering

### Unified System Integration
The template plugin is designed as part of the unified Nonix system where:
- **Template functionality serves as base** → Other interfaces (web, GUI, CLI, AI) can render templates
- **Clean abstractions** → Template rendering works across all interface types
- **AI-first design** → Templates can be used for AI prompt engineering and response formatting
- **Maximum extensibility** → Super slim, super fast template system that grows with your needs

## Quick Start

### 1. Add Template Plugin

The template plugin depends on the database plugin:

```python
settings.PLUGINS = [
    {"name": "db"},        # Required: database foundation
    {"name": "template"},  # Template plugin
    # ... other plugins
]
```

### 2. Configure Template Search Paths

Configure where to load templates from:

```python
# In your plugin or application configuration
template_config = {
    "template_search_paths": [
        "./templates",           # Local templates
        "/app/shared/templates", # Shared templates
        "./plugin_templates"     # Plugin-specific templates
    ]
}

# The plugin will automatically configure with these paths
```

### 3. Use Template Service

Inject the template service in your components:

```python
from nonix_di.resolve import NxInject
from nonix_template.services.template_service import TemplateService

class ContentRenderer:
    template_service: TemplateService = NxInject(TemplateService)

    async def render_page(self, template_name: str, data: dict):
        return await self.template_service.render_template(template_name, data)
```

### 4. Use Template Decorator (New!)

Automatically load templates from plugin directories:

```python
from nonix_template import templates
from nonix_plugin import BasePlugin

@templates()  # Auto-discovers ./your_plugin/templates/
class YourPlugin(BasePlugin):
    # Templates automatically loaded and available system-wide
    pass
```

### 5. Create and Manage Templates

Templates can be created via API or programmatically:

```python
# Create a template via service
template_data = {
    "name": "welcome_email",
    "description": "Welcome email template",
    "content": """
    <h1>Welcome {{ user.name }}!</h1>
    <p>Thank you for joining {{ site_name }}.</p>
    """,
    "context": {
        "site_name": "MyApp",
        "user": {"name": "Default User"}
    }
}

await template_service.create(template_data)
```

## Template Management

### Creating Templates

Templates combine content with optional context and inheritance:

```python
# Basic template
basic_template = {
    "name": "simple_message",
    "description": "A simple message template",
    "content": "Hello {{ name }}!",
    "context": {"name": "World"}
}

# Template with inheritance
child_template = {
    "name": "email_layout",
    "description": "Email layout with header/footer",
    "content": """
    {% extends "base_email" %}
    {% block content %}
    <div class="email-content">
        {{ custom_content }}
    </div>
    {% endblock %}
    """,
    "parent_template_id": 1  # Reference to parent template
}
```

### Template CRUD Operations

The service provides full CRUD operations:

```python
# Create
template = await template_service.create(template_data)

# Read
template = await template_service.get_one(template_id=1)
all_templates = await template_service.get_all({"page": 1, "per_page": 20})

# Update
updated = await template_service.update(template_id=1, update_data)

# Delete
await template_service.delete(template_id=1)
```

### Advanced Queries

```python
# Filter and sort
filtered = await template_service.get_all({
    "filter_name": "email_*",        # Name pattern matching
    "order_by": "created_at:desc",   # Sort by creation date
    "page": 1,
    "per_page": 10
})

# Search across fields
search_results = await template_service.search({
    "page": 1,
    "per_page": 20
}, "welcome email")
```

## Template Rendering

### Basic Rendering

Render templates by name or ID:

```python
# Render by name
html = await template_service.render_template("welcome_email", {
    "user": {"name": "John Doe"},
    "site_name": "MyApp"
})

# Render by ID
html = await template_service.render_template_by_id(1, context_data)

# Get raw content
content = await template_service.get_template_content("template_name")
```

### Context Management

Templates support flexible context merging:

```python
# Template has default context
template_context = {"site_name": "MyApp", "version": "1.0"}

# User provides additional context
user_context = {"user": {"name": "John"}, "current_year": 2024}

# Result: merged context with user context taking precedence
await template_service.render_template("email", user_context)
```

### Template Inheritance

Jinja2 inheritance allows template composition:

```python
# Base template (base_email.html)
base_content = """
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <header>Header</header>
    {% block content %}{% endblock %}
    <footer>Footer</footer>
</body>
</html>
"""

# Child template (welcome_email.html)
child_content = """
{% extends "base_email" %}
{% block content %}
<h1>Welcome {{ user.name }}!</h1>
<p>Welcome to {{ site_name }}</p>
{% endblock %}
"""
```

## Search Path Management

### Adding Search Paths

Configure where to load filesystem templates:

```python
# Add search paths
await template_service.add_search_path("./templates")
await template_service.add_search_path("/app/shared/templates")
await template_service.add_search_path("./plugin_templates")

# List current paths
paths = template_service.list_search_paths()
print("Template search paths:", paths)
```

### Search Path Priority

Templates are resolved in this order:
1. **Database templates** (highest priority)
2. **Filesystem templates** (searched in order of addition)
3. **Fallback to parent templates** (for inheritance)

### Managing Search Paths

```python
# Remove a path
template_service.remove_search_path("./old_templates")

# Clear all paths
template_service.clear_search_paths()

# List current paths
current_paths = template_service.list_search_paths()
```

## Advanced Features

### Template Caching

Templates are cached for performance:

```python
# Clear template cache if needed
template_service.clear_template_cache()

# Cache is automatically managed - templates reload when modified
```

### Available Templates

List all available templates with metadata:

```python
templates = await template_service.list_available_templates()

# Returns:
# {
#     "welcome_email": {
#         "id": 1,
#         "description": "Welcome email template",
#         "has_parent": false,
#         "parent_name": null,
#         "created_at": "2024-01-01T00:00:00"
#     }
# }
```

### Error Handling

Comprehensive error handling for template operations:

```python
try:
    result = await template_service.render_template("nonexistent", context)
except TemplateNotFoundError:
    print("Template not found")
except TemplateRenderingError as e:
    print(f"Rendering failed: {e}")
except InvalidContextError as e:
    print(f"Invalid context: {e}")
```

## Integration Examples

### Web Framework Integration

Use templates in FastAPI endpoints:

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from nonix_di.resolve import di_resolve
from nonix_template.services.template_service import TemplateService

app = FastAPI()

@app.get("/welcome/{name}", response_class=HTMLResponse)
async def welcome_page(name: str):
    template_service = di_resolve(TemplateService)

    html = await template_service.render_template("welcome_page", {
        "user_name": name,
        "current_time": datetime.now().isoformat()
    })

    return html
```

### Email Template Integration

Use templates for email rendering:

```python
class EmailService:
    def __init__(self):
        from nonix_di.resolve import NxInject
        self.template_service = NxInject(TemplateService)

    async def send_welcome_email(self, user_data):
        # Render email template
        html_content = await self.template_service.render_template(
            "welcome_email",
            {
                "user": user_data,
                "login_url": self.generate_login_url(user_data["id"])
            }
        )

        # Send email with rendered content
        await self.send_email(user_data["email"], "Welcome!", html_content)
```

### Content Management System

Build a CMS with template-driven content:

```python
class CMSService:
    def __init__(self):
        from nonix_di.resolve import NxInject
        self.template_service = NxInject(TemplateService)

    async def render_page(self, page_slug: str, context: dict = None):
        # Get page template from database
        page_data = await self.get_page_by_slug(page_slug)

        # Render with template system
        return await self.template_service.render_template(
            page_data["template_name"],
            {**page_data, **(context or {})}
        )

    async def create_page(self, template_name: str, content_data: dict):
        # Validate template exists
        available = await self.template_service.list_available_templates()
        if template_name not in available:
            raise ValueError(f"Template '{template_name}' not found")

        # Create page with template
        return await self.save_page(template_name, content_data)
```

## Best Practices

### Template Organization

```python
# Good: Organized template structure
templates/
├── base/
│   ├── layout.html
│   └── email_base.html
├── pages/
│   ├── home.html
│   ├── about.html
│   └── contact.html
├── components/
│   ├── header.html
│   ├── footer.html
│   └── navigation.html
└── emails/
    ├── welcome.html
    ├── password_reset.html
    └── newsletter.html
```

### Context Design

```python
# Good: Well-structured context
context = {
    "user": {
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {...}
    },
    "site": {
        "name": "MyApp",
        "url": "https://myapp.com",
        "version": "1.0.0"
    },
    "current_page": {
        "title": "Dashboard",
        "path": "/dashboard"
    }
}
```

### Error Handling

```python
# Good: Comprehensive error handling
class RobustTemplateService:
    async def safe_render(self, template_name: str, context: dict = None):
        try:
            return await self.template_service.render_template(template_name, context)
        except TemplateNotFoundError:
            # Fallback to default template
            return await self.render_default_template(context)
        except TemplateRenderingError as e:
            # Log error and return error template
            self.logger.error(f"Template rendering failed: {e}")
            return await self.render_error_template(context, str(e))
```

### Performance Optimization

```python
# Good: Cache frequently used templates
class CachedTemplateService:
    def __init__(self):
        self._cache = {}

    async def render_cached_template(self, name: str, context: dict):
        cache_key = f"{name}:{hash(str(context))}"

        if cache_key not in self._cache:
            self._cache[cache_key] = await self.template_service.render_template(name, context)

        return self._cache[cache_key]
```

## Troubleshooting

### Template Not Found

**Problem**: Template cannot be located

**Solutions**:
- Check template name spelling and case
- Verify template exists in database or filesystem
- Check search paths are configured correctly
- Use `list_available_templates()` to see available templates

### Rendering Errors

**Problem**: Template fails to render

**Solutions**:
- Validate Jinja2 syntax in template content
- Check context data structure matches template variables
- Ensure all required context variables are provided
- Use template debugging features

### Search Path Issues

**Problem**: Filesystem templates not loading

**Solutions**:
- Verify paths exist and are readable
- Check path permissions
- Use absolute paths when possible
- Validate path format (forward slashes)

### Inheritance Problems

**Problem**: Template inheritance not working

**Solutions**:
- Ensure parent template exists
- Check parent template name in child template
- Verify block names match between parent and child
- Use correct Jinja2 inheritance syntax

## Unified System Integration

### Cross-Interface Template Usage

The template system works seamlessly across all Nonix interfaces:

```python
# Web Interface
@app.get("/page")
async def web_page():
    return await template_service.render_template("page_template", web_context)

# CLI Interface
def cli_command():
    output = await template_service.render_template("cli_template", cli_context)
    print(output)

# GUI Interface
def gui_render():
    html = await template_service.render_template("gui_template", gui_context)
    webview_display(html)

# AI Interface
def ai_response():
    prompt = await template_service.render_template("ai_prompt", ai_context)
    response = await ai_service.generate(prompt)
    return response
```

### @templates Decorator

The `@templates` decorator provides automatic template loading with smart discovery:

#### Basic Usage

```python
from nonix_template import templates
from nonix_plugin import BasePlugin

@templates()  # Most common usage
class EmailPlugin(BasePlugin):
    # Automatically loads templates from ./email_plugin/templates/
    # if the directory exists
    pass
```

#### Advanced Usage

```python
# Custom directories only
@templates([
    "./email_templates",
    "/shared/company_templates"
], discover=False)
class EmailPlugin(BasePlugin):
    # Only loads from specified directories
    pass

# Custom directories + auto-discovery (default behavior)
@templates([
    "./local_templates",
    "./theme_templates"
], discover=True)  # discover=True is default
class ThemePlugin(BasePlugin):
    # Loads from custom directories + ./theme_plugin/templates/
    pass

# Relative paths are resolved relative to plugin directory
@templates([
    "./templates",        # ./your_plugin/templates/
    "../shared/templates" # ../shared/templates/
])
class ContentPlugin(BasePlugin):
    pass
```

#### Decorator Parameters

- **`directories`** (optional): List of directories to load templates from
  - Relative paths resolved relative to plugin directory
  - Absolute paths used as-is
  - Empty list `[]` disables custom directories

- **`discover`** (default: `True`): Auto-discover plugin's template directory
  - Looks for `./plugin_name/templates/` directory
  - Safely handles missing directories
  - Can be disabled with `discover=False`

#### Template Loading Priority

Templates are loaded in this order (last loaded wins for conflicts):

1. **Plugin auto-discovery**: `./plugin_name/templates/` (lowest priority)
2. **Custom directories**: In the order specified (highest priority)

#### Error Handling

The decorator gracefully handles common issues:

```python
# Missing directories are ignored (with warning)
@templates([
    "./templates",      # ✅ Loaded if exists
    "./missing_dir",    # ⚠️  Warning logged, skipped
    "/invalid/path"     # ⚠️  Warning logged, skipped
])
class RobustPlugin(BasePlugin):
    pass
```

#### Integration with Template Service

Decorated plugins automatically register their template directories with the global template service, making templates available system-wide:

```python
# Templates loaded by @templates() are available everywhere
@templates()
class MyPlugin(BasePlugin): pass

# In any other part of the system
template_service: TemplateService = NxInject(TemplateService)
html = await template_service.render_template("my_template", context)
```

## Key Principles

### Template as Universal Renderer
- **Template system** = Universal rendering engine for the entire ecosystem
- **Cross-interface compatibility** = Same templates work in web, GUI, CLI, AI
- **Flexible context** = Context merging allows interface-specific customization
- **Async-first** = Built for high-performance async rendering

### Database + Filesystem Hybrid
- **Database storage** = Template CRUD with full metadata
- **Filesystem loading** = Fast loading from disk with search paths
- **Hybrid approach** = Best of both worlds for different use cases

### AI-First Template Design
- **Prompt engineering** = Templates can format AI prompts
- **Response processing** = Templates can format AI responses
- **Dynamic context** = Templates adapt to AI conversation flow

**Remember**: The template plugin is the universal rendering foundation of the Nonix ecosystem. Its hybrid database/filesystem approach, combined with powerful Jinja2 rendering and async support, makes it the go-to solution for template rendering across all interfaces - from web pages to AI prompts to CLI outputs.

## Plugin Development Workflow

1. **Choose Template Approach** - Decide between database storage, filesystem loading, or hybrid
2. **Configure Search Paths** - Set up filesystem template locations
3. **Design Template Structure** - Plan template inheritance and context structure
4. **Create Templates** - Write Jinja2 templates with proper inheritance
5. **Implement Services** - Build services that use template rendering
6. **Add Error Handling** - Implement comprehensive error handling and fallbacks
7. **Test Rendering** - Verify templates render correctly with various contexts
8. **Optimize Performance** - Implement caching and monitor rendering performance
9. **Document Usage** - Create clear documentation for template usage patterns

The template plugin provides a powerful, flexible foundation for content rendering that scales from simple string interpolation to complex, inheritance-based template systems used across your entire application ecosystem.
