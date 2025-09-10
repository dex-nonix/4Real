# NxWeb Template Plugin

A powerful template rendering system for the NxWeb framework with database-backed templates and filesystem fallback support.

## Features

- 🔄 **Template Inheritance**: Full Jinja2 template inheritance with `{% extends %}` and `{% block %}`
- 🗄️ **Database Storage**: Store templates in database with versioning and metadata
- 📁 **Filesystem Fallback**: Automatic fallback to filesystem templates in registered search paths
- 🔍 **Flexible Resolution**: Template names with slashes work as folders and database identifiers
- 📝 **Multiple Formats**: Support for `.jinja2`, `.html`, `.txt`, and `.md` templates
- 🚀 **High Performance**: Smart caching for both database and filesystem templates
- 🔧 **Plugin Integration**: Clean API for other plugins to register template directories
- ⚡ **Async Support**: Full asynchronous template rendering

## Installation

The template plugin is automatically loaded when included in your `main.py`:

```python
settings.PLUGINS = [
    "db",           # Required dependency
    "template",     # This plugin
    # ... other plugins
]
```

### Dependencies

- **Required**: `db` plugin (provides database access)
- **Optional**: Other plugins can register template search paths

## Configuration

### Basic Configuration

```json
{
  "name": "template",
  "config": {
    "template_search_paths": [
      "/app/templates",
      "/shared/templates"
    ]
  }
}
```

### Advanced Configuration

```json
{
  "name": "template",
  "config": {
    "template_search_paths": [
      "/app/custom-templates",
      "/shared/company-templates",
      "./local-templates"
    ]
  }
}
```

## Usage

### Basic Template Rendering

```python
from nonix_di.di import InjectPlugin


class MyPlugin(BasePlugin):
    template_plugin: "NxWebTemplatePlugin" = InjectPlugin("template")

    async def generate_content(self):
        # Render template with context
        content = await self.template_plugin.render_template(
            "emails/welcome",
            context={"user": "John", "company": "Acme Corp"}
        )
        return content
```

### Template with ID

```python
# Render by database ID
content = await self.template_plugin.render_template_by_id(
    template_id=123,
    context={"data": "value"}
)
```

### Get Raw Template Content

```python
# Get template source without rendering
source = await self.template_plugin.get_template_content("emails/welcome")
```

## Search Path Management

### Adding Search Paths

```python
# Add custom template directories
await self.template_plugin.add_search_path("/path/to/templates")
await self.template_plugin.add_search_path("./relative/path")
await self.template_plugin.add_search_path("/shared/templates")
```

### Managing Search Paths

```python
# List all search paths
paths = self.template_plugin.list_search_paths()
print(paths)  # ["/path/to/templates", "/shared/templates"]

# Remove a search path
self.template_plugin.remove_search_path("/path/to/templates")

# Clear all search paths
self.template_plugin.clear_search_paths()
```

## Template Resolution

### Template Name Format

Template names can contain slashes and work in both contexts:

```python
# Database template name
"emails/welcome"

# Filesystem template path
emails/welcome.jinja2  # or .html, .txt, .md
```

### Resolution Hierarchy

Templates are resolved in this order:

1. **Database** (highest priority)
   - Exact name match in `templates` table
   - Example: `"emails/welcome"` → database record

2. **Filesystem** (fallback)
   - Searches each registered path in order
   - Tries multiple extensions: `.jinja2`, `.html`, `.txt`, `.md`
   - Example: `"emails/welcome"` → `emails/welcome.jinja2`

### Example Resolution

```python
# Template name: "admin/users/list"

# 1. Database lookup:
# SELECT * FROM templates WHERE name = "admin/users/list"

# 2. Filesystem lookup (if not found in DB):
# /app/templates/admin/users/list.jinja2
# /app/templates/admin/users/list.html
# /shared/templates/admin/users/list.jinja2
# /shared/templates/admin/users/list.html
```

## Template Inheritance

### Base Template Example

**templates/base/layout.jinja2:**
```jinja2
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <header>{% block header %}{% endblock %}</header>
    <main>{% block content %}{% endblock %}</main>
    <footer>{% block footer %}© 2024{% endblock %}</footer>
</body>
</html>
```

### Child Template Example

**templates/pages/home.jinja2:**
```jinja2
{% extends "base/layout" %}

{% block title %}Home Page{% endblock %}

{% block header %}
<h1>Welcome to Our Site</h1>
{% endblock %}

{% block content %}
<p>This is the home page content.</p>
{% endblock %}
```

### Usage

```python
# Render child template with inheritance
content = await self.template_plugin.render_template(
    "pages/home",
    context={"user": "John"}
)
```

## Database Schema

### Templates Table

```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    content TEXT NOT NULL,
    context JSON,
    parent_template_id INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (parent_template_id) REFERENCES templates(id)
);
```

### Fields

- **name**: Unique template identifier (can contain slashes)
- **description**: Optional human-readable description
- **content**: Template source code
- **context**: Optional default JSON context
- **parent_template_id**: For template inheritance relationships

## API Reference

### NxWebTemplatePlugin Methods

#### Template Rendering
- `render_template(name, context=None)` - Render by name
- `render_template_by_id(id, context=None)` - Render by ID
- `get_template_content(name)` - Get raw template source

#### Search Path Management
- `add_search_path(path)` - Add template search directory
- `remove_search_path(path)` - Remove search directory
- `list_search_paths()` - List all search directories
- `clear_search_paths()` - Remove all search directories

#### Template Discovery
- `list_available_templates()` - List all templates with metadata

#### Cache Management
- `clear_template_cache()` - Clear all template caches

## File Structure

```
/plugin/
├── README.md                    # This file
├── plugin.json                  # Plugin metadata
├── plugin.py                    # Main plugin class
├── models/
│   └── template.py             # Template database model
└── services/
    └── template/
        ├── __init__.py
        ├── template_schemas.py    # Pydantic schemas
        ├── template_service.py    # CRUD API service
        ├── template_renderer.py   # Rendering engine
        ├── database_template_loader.py  # Jinja2 loader
        └── template_exceptions.py  # Custom exceptions
```

## Error Handling

### TemplateNotFoundError
Raised when a template cannot be found in database or filesystem.

### TemplateRenderingError
Raised when template rendering fails due to syntax errors or context issues.

### TemplatePathError
Raised when adding invalid search paths (non-existent, not a directory, no permissions).

## Best Practices

### 1. Template Organization

```
/templates/
├── base/           # Base templates for inheritance
├── emails/         # Email templates
├── pages/          # Page templates
├── components/     # Reusable components
└── layouts/        # Layout templates
```

### 2. Naming Conventions

- Use lowercase with hyphens: `user-profile.html`
- Use slashes for organization: `emails/welcome.html`
- Be descriptive: `admin/user-management.html`

### 3. Context Management

```python
# Good: Use descriptive context keys
context = {
    "user_name": user.name,
    "user_email": user.email,
    "company_name": "Acme Corp",
    "current_year": 2024
}

# Avoid: Generic keys
context = {
    "name": user.name,
    "email": user.email,
    "company": "Acme Corp"
}
```

### 4. Search Path Strategy

```python
# Add search paths in priority order
await template_plugin.add_search_path("./templates")        # Plugin-specific
await template_plugin.add_search_path("/shared/templates")  # Shared across plugins
await template_plugin.add_search_path("/app/templates")     # Application-wide
```

### 5. Template Inheritance

```jinja2
{# Base template: base/layout.jinja2 #}
<!DOCTYPE html>
<html>
<body>
    {% block header %}{% endblock %}
    {% block content %}{% endblock %}
    {% block footer %}{% endblock %}
</body>
</html>

{# Child template: pages/home.jinja2 #}
{% extends "base/layout" %}

{% block header %}<h1>Home Page</h1>{% endblock %}
{% block content %}<p>Welcome!</p>{% endblock %}
```

## Performance Considerations

### Caching
- Templates are cached after first load
- Database templates cached separately from filesystem templates
- Cache automatically invalidated when search paths change

### Optimization Tips
- Use template inheritance to reduce duplication
- Prefer database templates for frequently changing content
- Use filesystem templates for static content
- Register search paths in priority order

## Troubleshooting

### Common Issues

1. **Template not found**
   - Check template name spelling
   - Verify search paths are registered
   - Confirm template file exists with correct extension

2. **Inheritance not working**
   - Ensure parent template exists
   - Check template name in `{% extends %}` tag
   - Verify file extensions match

3. **Context errors**
   - Check variable names in templates
   - Verify context dictionary structure
   - Use template debugging features

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('nonix_template').setLevel(logging.DEBUG)
```

## Contributing

When adding new features:

1. Update this README with new functionality
2. Add comprehensive tests
3. Follow existing code patterns
4. Update error handling as needed

## License

This plugin is part of the NxWeb framework ecosystem.
