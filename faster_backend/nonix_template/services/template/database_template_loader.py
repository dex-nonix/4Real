from typing import List, Tuple, Optional
from jinja2 import TemplateNotFound
from pathlib import Path
import asyncio
import os

from .template_exceptions import TemplateNotFoundError


class DatabaseTemplateLoader:
    """Custom Jinja2 loader that loads templates from database and filesystem with inheritance support"""

    # Supported template file extensions
    TEMPLATE_EXTENSIONS = ['.jinja2', '.html', '.txt', '.md']

    def __init__(self, search_paths: Optional[List[Path]] = None):
        self._search_paths = search_paths or []
        self._cache = {}  # template_name -> (content, filename, uptodate)
        self._inheritance_cache = {}  # template_name -> resolved_content

    def get_source(self, environment, template_name) -> Tuple[str, str, bool]:
        """
        Load template source from database first, then filesystem fallback
        Returns: (source, filename, uptodate)
        """
        try:
            # Check cache first
            if template_name in self._cache:
                source, filename, uptodate = self._cache[template_name]
                return source, filename, uptodate

            # Step 1: Try to load from database
            try:
                template = self._load_template_sync(template_name)
                if template:
                    # Store in cache
                    source = template.content
                    filename = f"database:{template.name}"
                    uptodate = True  # Database templates are always considered up-to-date

                    self._cache[template_name] = (source, filename, uptodate)
                    return source, filename, uptodate
            except TemplateNotFoundError:
                pass  # Continue to filesystem fallback

            # Step 2: Try to load from filesystem paths
            source, filename, uptodate = self._load_from_filesystem(template_name)

            # Store in cache
            self._cache[template_name] = (source, filename, uptodate)
            return source, filename, uptodate

        except TemplateNotFoundError:
            raise TemplateNotFound(template_name)

    def _load_from_filesystem(self, template_name: str) -> Tuple[str, str, bool]:
        """
        Load template from filesystem search paths
        Returns: (source, filename, uptodate)
        """
        if not self._search_paths:
            raise TemplateNotFoundError(template_name)

        # Convert template name with "/" to filesystem path
        # e.g., "emails/welcome" becomes "emails/welcome"
        template_path = Path(template_name)

        # Try each search path
        for search_path in self._search_paths:
            # Try each file extension
            for ext in self.TEMPLATE_EXTENSIONS:
                file_path = search_path / template_path.with_suffix(ext)

                if file_path.exists() and file_path.is_file():
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source = f.read()

                        # For now, consider files up-to-date
                        uptodate = True

                        filename = f"filesystem:{file_path}"
                        return source, filename, uptodate

                    except (IOError, OSError):
                        # Log error but continue to next file
                        continue

        # No template found in any search path
        raise TemplateNotFoundError(template_name)

    def update_search_paths(self, search_paths: List[Path]):
        """
        Update the search paths used by the loader
        """
        self._search_paths = search_paths.copy()
        # Clear filesystem cache when paths change
        # Keep database cache as it's still valid
        fs_keys = [k for k, (_, filename, _) in self._cache.items()
                  if filename.startswith('filesystem:')]
        for key in fs_keys:
            del self._cache[key]

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

    def clear_filesystem_cache(self):
        """Clear only filesystem template cache"""
        fs_keys = [k for k, (_, filename, _) in self._cache.items()
                  if filename.startswith('filesystem:')]
        for key in fs_keys:
            del self._cache[key]

    def clear_database_cache(self):
        """Clear only database template cache"""
        db_keys = [k for k, (_, filename, _) in self._cache.items()
                  if filename.startswith('database:')]
        for key in db_keys:
            del self._cache[key]

    def add_template_to_cache(self, template_name: str, content: str):
        """Manually add template to cache (useful for testing)"""
        filename = f"database:{template_name}"
        self._cache[template_name] = (content, filename, True)
