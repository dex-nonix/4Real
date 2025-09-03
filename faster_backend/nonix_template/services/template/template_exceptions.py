class TemplateError(Exception):
    """Base exception for template-related errors"""
    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a template cannot be found by name or ID"""

    def __init__(self, template_name_or_id):
        self.template_name_or_id = template_name_or_id
        super().__init__(f"Template '{template_name_or_id}' not found")


class CircularInheritanceError(TemplateError):
    """Raised when there's a circular inheritance relationship between templates"""

    def __init__(self, template_chain):
        self.template_chain = template_chain
        super().__init__(f"Circular inheritance detected: {' -> '.join(template_chain)}")


class TemplateSyntaxError(TemplateError):
    """Raised when there's a syntax error in template content"""

    def __init__(self, template_name, original_error):
        self.template_name = template_name
        self.original_error = original_error
        super().__init__(f"Syntax error in template '{template_name}': {original_error}")


class InvalidContextError(TemplateError):
    """Raised when template context is invalid"""

    def __init__(self, message):
        super().__init__(f"Invalid template context: {message}")


class TemplateRenderingError(TemplateError):
    """Raised when template rendering fails"""

    def __init__(self, template_name, original_error):
        self.template_name = template_name
        self.original_error = original_error
        super().__init__(f"Failed to render template '{template_name}': {original_error}")
