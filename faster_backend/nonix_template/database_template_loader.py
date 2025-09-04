from typing import List, Tuple, Optional
from jinja2 import TemplateNotFound
from jinja2_async_environment import AsyncBaseLoader
from aiopath import AsyncPath
from pathlib import Path
from sqlalchemy import select
import aiofiles

from nonix_web_db import AsyncSessionLocal
from .template_exceptions import TemplateNotFoundError
from nonix_template.models.template import Template as DbTemplate


class DatabaseTemplateLoader(AsyncBaseLoader):
    """Custom Jinja2 loader that loads templates from database and filesystem with inheritance support"""

    # Supported template file extensions
    TEMPLATE_EXTENSIONS = ['.jinja2', '.html', '.txt', '.md']

    def __init__(self, search_paths: Optional[List[Path]] = None):
        self._search_paths = search_paths or []
        self._cache = {}  # template_name -> (content, path, uptodate)
        self._inheritance_cache = {}  # template_name -> resolved_content

    async def get_source(self, template: AsyncPath) -> Tuple[str, AsyncPath, bool]:
        """
        Load template source from database first, then filesystem fallback (async)
        Returns: (source, filename, uptodate)
        """
        template_name = str(template)
        print(f"DEBUG: get_source called with template: {template}, template_name: {template_name}")
        try:
            # Check cache first
            if template_name in self._cache:
                source, path, uptodate = self._cache[template_name]
                return source, path, uptodate

            # Step 1: Try to load from database
            try:
                template_obj = await self._load_template_by_name(template_name)
                if template_obj:
                    print(f"DEBUG: Found template '{template_name}' in database")
                    # Store in cache
                    source = template_obj.content
                    path = AsyncPath(template_name)
                    uptodate = None  # Database templates are always considered up-to-date

                    self._cache[template_name] = (source, path, uptodate)
                    return source, path, uptodate
                else:
                    print(f"DEBUG: Template '{template_name}' not found in database, trying filesystem")
            except Exception as e:
                print(f"DEBUG: Database lookup failed for '{template_name}': {e}, trying filesystem")

            # Step 2: Try to load from filesystem paths
            print(f"DEBUG: Current search paths: {[str(p) for p in self._search_paths]}")
            source, path, uptodate = await self._load_from_filesystem_async(template_name)

            # Store in cache
            self._cache[template_name] = (source, path, uptodate)
            return source, path, uptodate

        except TemplateNotFoundError:
            raise TemplateNotFound(template_name)

    async def _load_from_filesystem_async(self, template_name: str) -> Tuple[str, AsyncPath, bool]:
        """
        Load template from filesystem search paths (async)
        Returns: (source, filename, uptodate)
        """
        print(f"DEBUG: Loading from filesystem for '{template_name}'")
        if not self._search_paths:
            print("DEBUG: No search paths configured!")
            raise TemplateNotFoundError(template_name)

        # Try each search path
        for search_path in self._search_paths:
            print(f"DEBUG: Checking search path: {search_path}")
            # Try each file extension
            for ext in self.TEMPLATE_EXTENSIONS:
                # Preserve the directory structure by adding extension to the full path
                file_path = search_path / (template_name + ext)
                print(f"DEBUG: Checking file: {file_path}")

                if file_path.exists() and file_path.is_file():
                    print(f"DEBUG: Found template file: {file_path}")
                    try:
                        # Read file content asynchronously
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            source = await f.read()

                        # For now, consider files up-to-date
                        uptodate = None

                        path = AsyncPath(file_path)
                        return source, path, uptodate

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
        fs_keys = [k for k, (_, path, _) in self._cache.items()
                  if str(path).startswith('/')]  # filesystem paths start with /
        for key in fs_keys:
            del self._cache[key]



    async def _load_template_by_name(self, template_name: str):
        """Load template from database by name"""
        async with AsyncSessionLocal() as session:
            stmt = select(DbTemplate).where(DbTemplate.name == template_name)
            result = await session.execute(stmt)
            template = result.scalar_one_or_none()

            if not template:
                return None

            # Load parent template if exists (for inheritance resolution)
            if template.parent_template_id:
                parent_stmt = select(DbTemplate).where(DbTemplate.id == template.parent_template_id)
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
        fs_keys = [k for k, (_, path, _) in self._cache.items()
                  if str(path).startswith('/')]  # filesystem paths start with /
        for key in fs_keys:
            del self._cache[key]

    def clear_database_cache(self):
        """Clear only database template cache"""
        db_keys = [k for k, (_, path, _) in self._cache.items()
                  if not str(path).startswith('/')]  # database paths don't start with /
        for key in db_keys:
            del self._cache[key]

    def add_template_to_cache(self, template_name: str, content: str):
        """Manually add template to cache (useful for testing)"""
        path = AsyncPath(template_name)
        self._cache[template_name] = (content, path, True)
