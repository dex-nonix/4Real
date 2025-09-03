from typing import Dict, Any, TYPE_CHECKING

from nonix_web.plugin.base_plugin import BasePlugin, api_services
from .services.template import TemplateService
from .services.template.template_renderer import TemplateRenderer

if TYPE_CHECKING:
    from nonix_web.server import NxWebServer


@api_services([
    TemplateService
])
class NxWebTemplatePlugin(BasePlugin):
    template_renderer: TemplateRenderer = None

    def _configure(self, server: "NxWebServer", config: Dict[str, Any]):
        """Initialize template renderer during plugin configuration"""
        self.template_renderer = TemplateRenderer()



    # Public API methods for consumers
    async def render_template(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template by name with optional context

        Args:
            template_name: Name of the template to render
            context: Optional context dictionary to pass to the template

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateRenderingError: If rendering fails
        """
        if not self.template_renderer:
            raise RuntimeError("Template renderer not initialized")

        return await self.template_renderer.render_by_name(template_name, context)

    async def render_template_by_id(self, template_id: int, context: Dict[str, Any] = None) -> str:
        """
        Render a template by ID with optional context

        Args:
            template_id: ID of the template to render
            context: Optional context dictionary to pass to the template

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateRenderingError: If rendering fails
        """
        if not self.template_renderer:
            raise RuntimeError("Template renderer not initialized")

        return await self.template_renderer.render_by_id(template_id, context)

    async def get_template_content(self, template_name: str) -> str:
        """
        Get raw template content without rendering

        Args:
            template_name: Name of the template

        Returns:
            Raw template content as string

        Raises:
            TemplateNotFoundError: If template doesn't exist
        """
        if not self.template_renderer:
            raise RuntimeError("Template renderer not initialized")

        return await self.template_renderer.get_template_content(template_name)

    async def list_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available templates with metadata

        Returns:
            Dictionary mapping template names to metadata
        """
        if not self.template_renderer:
            raise RuntimeError("Template renderer not initialized")

        return await self.template_renderer.list_available_templates()

    def clear_template_cache(self):
        """Clear the template cache"""
        if self.template_renderer:
            self.template_renderer.clear_cache()
