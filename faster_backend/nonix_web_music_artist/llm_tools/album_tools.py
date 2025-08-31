from typing import Dict, Any, Optional
from datetime import date

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.album import Album
from ..services.album.album_schemas import AlbumCreate, AlbumUpdate


class AlbumToolService(AgenticCrudTools):
    """Album CRUD operations for artists."""

    prefix = "album"
    config = CRUDConfig(
        model=Album,
        create_schema=AlbumCreate,
        update_schema=AlbumUpdate,
        response_schema=AlbumCreate,  # Use AlbumCreate as response schema
        filters=FilterConfig(allowed_fields=['title', 'release_date', 'artist_id']),
        sorting=SortingConfig(default_sort='release_date', allowed_fields=['title', 'release_date', 'created_at']),
        validation=ValidationConfig(unique_fields=[])
    )

    @tool("create")
    async def create_album(self, artist_id: int, title: str, release_date: Optional[date] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new album for the artist."""
        return await self.create(
            title=title,
            artist_id=artist_id,
            release_date=release_date,
            description=description
        )

    @tool("update")
    async def update_album(self, artist_id: int, album_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing album's details."""
        return await self.update(
            item_id=album_id,
            title=title,
            description=description
        )

    @tool("delete")
    async def delete_album(self, artist_id: int, album_id: int) -> Dict[str, Any]:
        """Delete an album and all its tracks."""
        return await self.delete(item_id=album_id)

    @tool("get")
    async def get_album(self, artist_id: int, album_id: int) -> Dict[str, Any]:
        """Get details of a single album."""
        return await self.get(item_id=album_id)

    @tool("list")
    async def list_albums(self, artist_id: int) -> Dict[str, Any]:
        """List all albums in the artist's catalog."""
        return await self.list(filters=[self.config.model.artist_id == artist_id])


# Create an instance for the plugin to use
album_tool_service = AlbumToolService()
