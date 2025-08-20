from __future__ import annotations

import os

from jinja2 import Template


class SwaggerUIGenerator:
    """Handles Swagger UI HTML generation for the API documentation."""

    def __init__(self) -> None:
        pass

    def generate_swagger_ui(self, current_filter: str = None) -> str:
        """Generate Swagger UI HTML page with service filtering using Jinja2 template"""

        # Get the template file path
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'swagger_ui.html')

        # Read template and render - NO FALLBACK, just fail if it doesn't work
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Create Jinja2 template and render
        template = Template(template_content)
        return template.render(current_filter=current_filter)
