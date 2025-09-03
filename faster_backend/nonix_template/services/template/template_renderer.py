from typing import Dict, Any, Optional, Union
from jinja2 import Environment, Template
import asyncio
from sqlalchemy import select

from .database_template_loader import DatabaseTemplateLoader
from .template_exceptions import TemplateNotFoundError, TemplateRenderingError, InvalidContextError


class TemplateRenderer:
    """Handles template rendering with inheritance support"""

    def __init__(self, search_paths=None):
        self.loader = DatabaseTemplateLoader(search_paths)
        self.env = Environment(
            loader=self.loader,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            enable_async=True
        )

    async def render_by_name(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Render template by name with optional context"""
        try:
            template = await self._get_template_by_name(template_name)
            return await self._render_template(template, context)
        except Exception as e:
            if isinstance(e, TemplateNotFoundError):
                raise
            raise TemplateRenderingError(template_name, str(e))

    async def render_by_id(self, template_id: int, context: Optional[Dict[str, Any]] = None) -> str:
        """Render template by ID with optional context"""
        try:
            template = await self._get_template_by_id(template_id)
            return await self._render_template(template, context)
        except Exception as e:
            raise TemplateRenderingError(f"id:{template_id}", str(e))

    async def render_template_object(self, template, context: Optional[Dict[str, Any]] = None) -> str:
        """Render Template model instance"""
        return await self._render_template(template, context)

    async def get_template_content(self, template_name: str) -> str:
        """Get raw template content without rendering"""
        template = await self._get_template_by_name(template_name)
        return template.content

    async def list_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """List all available templates with metadata"""
        from nonix_web_db import AsyncSessionLocal
        from ...models.template import Template

        async with AsyncSessionLocal() as session:
            # Eager load parent template relationship
            stmt = select(Template).outerjoin(Template.parent_template)
            result = await session.execute(stmt)
            templates = result.unique().scalars().all()

            template_info = {}
            for template in templates:
                template_info[template.name] = {
                    'id': template.id,
                    'description': template.description,
                    'has_parent': template.parent_template_id is not None,
                    'parent_name': template.parent_template.name if template.parent_template else None,
                    'created_at': template.created_at.isoformat() if template.created_at else None
                }

            return template_info

    async def _get_template_by_name(self, template_name: str):
        """Get template by name"""
        from nonix_web_db import AsyncSessionLocal
        from ...models.template import Template

        async with AsyncSessionLocal() as session:
            stmt = select(Template).where(Template.name == template_name)
            result = await session.execute(stmt)
            template = result.scalar_one_or_none()

            if not template:
                raise TemplateNotFoundError(template_name)

            return template

    async def _get_template_by_id(self, template_id: int):
        """Get template by ID"""
        from nonix_web_db import AsyncSessionLocal
        from ...models.template import Template

        async with AsyncSessionLocal() as session:
            stmt = select(Template).where(Template.id == template_id)
            result = await session.execute(stmt)
            template = result.scalar_one_or_none()

            if not template:
                raise TemplateNotFoundError(f"id:{template_id}")

            return template

    async def _render_template(self, template, context: Optional[Dict[str, Any]] = None) -> str:
        """Render a template with context"""
        # Merge contexts: template default context + user context
        merged_context = self._merge_contexts(template.context, context)

        # Create Jinja2 template
        jinja_template = self.env.from_string(template.content)

        # Render template
        try:
            rendered = await jinja_template.render_async(**merged_context)
            return rendered.strip()
        except Exception as e:
            raise TemplateRenderingError(template.name, str(e))

    def _merge_contexts(self, template_context: Optional[Dict[str, Any]],
                       user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge template and user contexts with proper precedence"""
        merged = {}

        # Start with template default context
        if template_context:
            if not isinstance(template_context, dict):
                raise InvalidContextError("Template context must be a dictionary")
            merged.update(template_context)

        # Override with user context
        if user_context:
            if not isinstance(user_context, dict):
                raise InvalidContextError("User context must be a dictionary")
            merged.update(user_context)

        return merged

    def clear_cache(self):
        """Clear template cache"""
        self.loader.clear_cache()
