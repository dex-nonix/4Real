import os
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..router.template_schemas import TemplateCreate, TemplateUpdate, TemplateInDbModel
from ..models.template import Template
from ..template.template_renderer import TemplateRenderer

if TYPE_CHECKING:
    from ..plugin import TemplatePathError


class TemplateService(BaseCrudService):
    """
    Service for template CRUD operations and business logic.
    Contains all template management functionality including rendering and search path management.
    """
    config = CRUDConfig(
        model=Template,
        create_schema=TemplateCreate,
        update_schema=TemplateUpdate,
        response_schema=TemplateInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'description']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at', 'updated_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name', 'description']
        )
    )

    template_renderer: TemplateRenderer = None
    _search_paths: List[Path] = None

    def __init__(self):
        super().__init__()
        self._search_paths = []

    def configure_renderer(self, search_paths: List[str] = None):
        """Initialize template renderer with search paths"""
        if search_paths:
            for path in search_paths:
                try:
                    self.add_search_path(path)
                except Exception as e:
                    self._logger.warning(f"Failed to add search path '{path}': {e}")

        self.template_renderer = TemplateRenderer(self._search_paths)

    # Search path management methods
    def add_search_path(self, path: str):
        """
        Add a filesystem path for template fallback search

        Args:
            path: Filesystem path to add for template search

        Raises:
            TemplatePathError: If path is invalid or inaccessible
        """
        try:
            path_obj = Path(path).resolve()

            # Validate path exists and is a directory
            if not path_obj.exists():
                raise TemplatePathError(f"Path does not exist: {path}")

            if not path_obj.is_dir():
                raise TemplatePathError(f"Path is not a directory: {path}")

            # Check read access
            if not os.access(path_obj, os.R_OK):
                raise TemplatePathError(f"No read access to path: {path}")

            # Add if not already present
            if path_obj not in self._search_paths:
                self._search_paths.append(path_obj)
                self._logger.info(f"Added template search path: {path_obj}")

                # Update loader with new search paths
                if self.template_renderer and hasattr(self.template_renderer.loader, 'update_search_paths'):
                    self.template_renderer.loader.update_search_paths(self._search_paths)
            else:
                self._logger.debug(f"Search path already exists: {path_obj}")

        except Exception as e:
            if isinstance(e, TemplatePathError):
                raise
            raise TemplatePathError(f"Invalid search path '{path}': {str(e)}")

    def remove_search_path(self, path: str):
        """
        Remove a filesystem path from template search

        Args:
            path: Filesystem path to remove
        """
        path_obj = Path(path).resolve()
        if path_obj in self._search_paths:
            self._search_paths.remove(path_obj)
            self._logger.info(f"Removed template search path: {path_obj}")

            # Update loader with updated search paths
            if self.template_renderer and hasattr(self.template_renderer.loader, 'update_search_paths'):
                self.template_renderer.loader.update_search_paths(self._search_paths)

    def list_search_paths(self) -> List[str]:
        """
        List all registered template search paths

        Returns:
            List of search path strings
        """
        return [str(path) for path in self._search_paths]

    def clear_search_paths(self):
        """
        Clear all template search paths
        """
        self._search_paths.clear()
        self._logger.info("Cleared all template search paths")

        # Update loader
        if self.template_renderer and hasattr(self.template_renderer.loader, 'update_search_paths'):
            self.template_renderer.loader.update_search_paths(self._search_paths)

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
