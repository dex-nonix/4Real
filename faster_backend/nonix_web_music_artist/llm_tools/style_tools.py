from typing import Dict, Any, Optional

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.style import Style
from ..services.style.style_schemas import StyleCreate, StyleUpdate


class StyleToolService(AgenticCrudTools):
    """Style management operations for artists."""

    prefix = "style"
    config = CRUDConfig(
        model=Style,
        create_schema=StyleCreate,
        update_schema=StyleUpdate,
        response_schema=StyleCreate,  # Use StyleCreate as response schema
        filters=FilterConfig(allowed_fields=['name', 'description', 'category']),
        sorting=SortingConfig(default_sort='name', allowed_fields=['name', 'category', 'created_at']),
        validation=ValidationConfig(unique_fields=['name'])
    )

    @tool("create")
    async def create_style(self, name: str, description: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Create a new music style/genre."""
        return await self.create(
            name=name,
            description=description,
            category=category
        )

    @tool("update")
    async def update_style(self, style_id: int, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing style's details."""
        return await self.update(
            item_id=style_id,
            name=name,
            description=description,
            category=category
        )

    @tool("delete")
    async def delete_style(self, style_id: int) -> Dict[str, Any]:
        """Delete a style."""
        return await self.delete(item_id=style_id)

    @tool("get")
    async def get_style(self, style_id: int) -> Dict[str, Any]:
        """Get details of a single style."""
        return await self.get(item_id=style_id)

    @tool("list")
    async def list_styles(self) -> Dict[str, Any]:
        """List all available styles."""
        return await self.list()

    @tool("list_by_category")
    async def list_styles_by_category(self, category: str) -> Dict[str, Any]:
        """List styles by category."""
        return await self.list(filters=[self.config.model.category == category])

    @tool("search")
    async def search_styles(self, query: str) -> Dict[str, Any]:
        """Search styles by name or description."""
        return await self.list(filters=[
            self.config.model.name.ilike(f"%{query}%")
        ])


# Create an instance for the plugin to use
style_tool_service = StyleToolService()
