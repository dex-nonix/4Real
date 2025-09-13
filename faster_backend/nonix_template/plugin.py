from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from .router.template_router import TemplateRouter
from .services.template_service import TemplateService
from .template.template_renderer import TemplateRenderer


@web_routers([
    TemplateRouter
])
@injectables([
    TemplateService,
    TemplateRenderer
])
class NxWebTemplatePlugin(BasePlugin):
    template_service: TemplateService = NxInject(TemplateService)
    template_renderer: TemplateRenderer = NxInject(TemplateRenderer)

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def _configure(self, config: Dict[str, Any]):
        """Initialize template renderer and services during plugin configuration"""
        # Add default search paths from config
        default_paths = config.get('template_search_paths', [])

        # Configure the template service with search paths and renderer
        self.template_service._configure_renderer(default_paths)
