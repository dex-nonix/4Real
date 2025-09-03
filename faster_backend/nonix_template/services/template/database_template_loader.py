from typing import List, Tuple, Any
from jinja2 import TemplateNotFound
import asyncio

from .template_exceptions import TemplateNotFoundError, CircularInheritanceError


class DatabaseTemplateLoader:
    """Custom Jinja2 loader that loads templates from the database with inheritance support"""

    def __init__(self):
        self._cache = {}  # template_name -> (content, filename, uptodate)
        self._inheritance_cache = {}  # template_name -> resolved_content

    def get_source(self, environment, template_name) -> Tuple[str, str, bool]:
        """
        Load template source from database
        Returns: (source, filename, uptodate)
        """
        try:
            # Check cache first
            if template_name in self._cache:
                source, filename, uptodate = self._cache[template_name]
                return source, filename, uptodate

            # Load template from database
            template = self._load_template_sync(template_name)
            if not template:
                raise TemplateNotFound(template_name)

            # Store in cache
            source = template.content
            filename = f"database:{template.name}"
            uptodate = True  # Database templates are always considered up-to-date

            self._cache[template_name] = (source, filename, uptodate)
            return source, filename, uptodate

        except TemplateNotFoundError:
            raise TemplateNotFound(template_name)

    def _load_template_sync(self, template_name: str):
        """Load template from database synchronously"""
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async method in the event loop
        return loop.run_until_complete(self._load_template_by_name(template_name))

    async def _load_template_by_name(self, template_name: str):
        """Load template from database by name"""
        # Get async session
        from nonix_web_db import AsyncSessionLocal
        from sqlalchemy import select

        async with AsyncSessionLocal() as session:
            from ...models.template import Template

            stmt = select(Template).where(Template.name == template_name)
            result = await session.execute(stmt)
            template = result.scalar_one_or_none()

            if not template:
                return None

            # Load parent template if exists (for inheritance resolution)
            if template.parent_template_id:
                parent_stmt = select(Template).where(Template.id == template.parent_template_id)
                parent_result = await session.execute(parent_stmt)
                template.parent_template = parent_result.scalar_one_or_none()

            return template

    def list_templates(self) -> List[str]:
        """List all available template names"""
        # This would need to be async, but Jinja2 expects sync method
        # We'll implement this as a cached sync method
        if not hasattr(self, '_template_names'):
            # For now, return empty list - this would be populated during template operations
            self._template_names = []
        return self._template_names

    def clear_cache(self):
        """Clear template cache"""
        self._cache.clear()
        self._inheritance_cache.clear()

    def add_template_to_cache(self, template_name: str, content: str):
        """Manually add template to cache (useful for testing)"""
        filename = f"database:{template_name}"
        self._cache[template_name] = (content, filename, True)
