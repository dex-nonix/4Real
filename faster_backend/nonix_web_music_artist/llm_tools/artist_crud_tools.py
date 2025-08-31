from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.album import Album
from ..models.artist import Artist
from ..services.album.album_schemas import AlbumCreate, AlbumUpdate


# Create a CRUD config for album operations
album_crud_config = CRUDConfig(
    model=Album,
    create_schema=AlbumCreate,
    update_schema=AlbumUpdate,
    filters=FilterConfig(allowed_fields=['title', 'release_date', 'artist_id']),
    sorting=SortingConfig(default_sort='release_date', allowed_fields=['title', 'release_date', 'created_at']),
    validation=ValidationConfig(unique_fields=[])
)


class AlbumToolService(AgenticCrudTools):
    """Album CRUD operations for artists using generic CRUD base."""

    def __init__(self):
        super().__init__(Album, album_crud_config)

    @tool("album:create")
    async def create_album(self, artist_id: int, title: str, release_date: Optional[date] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new album for the artist.

        This function creates a new album in the artist's catalog with the provided details.

        Args:
            artist_id: The artist's ID (auto-bound by AgenticToolManager)
            title: The album title
            release_date: Optional release date for the album
            description: Optional description of the album

        Returns:
            Dictionary containing the created album information
        """
        # Create album data
        album_data = AlbumCreate(
            title=title,
            artist_id=artist_id,
            release_date=release_date,
            description=description
        )

        # Use CRUD operations to create album
        result = await self.create(album_data)
        return {
            "success": True,
            "album": result.to_dict(),
            "message": f"Album '{title}' created successfully"
        }

    @tool("album:update")
    async def update_album(self, artist_id: int, album_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing album's details.

        This function updates the specified album with new title and/or description.

        Args:
            artist_id: The artist's ID (auto-bound by AgenticToolManager)
            album_id: The ID of the album to update
            title: Optional new title for the album
            description: Optional new description for the album

        Returns:
            Dictionary containing the updated album information
        """
        # First verify the album belongs to this artist
        async with AsyncSessionLocal() as session:
            album_result = await session.execute(
                select(Album).where(Album.id == album_id, Album.artist_id == artist_id)
            )
            album = album_result.scalar_one_or_none()

            if not album:
                return {
                    "success": False,
                    "error": "Album not found or doesn't belong to this artist"
                }

            # Create update data
            update_data = AlbumUpdate()
            if title is not None:
                update_data.title = title
            if description is not None:
                update_data.description = description

            # Use CRUD operations to update album
            result = await self.update(album_id, update_data)
            return {
                "success": True,
                "album": result.to_dict(),
                "message": "Album updated successfully"
            }

    @tool("album:delete")
    async def delete_album(self, artist_id: int, album_id: int) -> Dict[str, Any]:
        """Delete an album and all its tracks.

        This function removes the specified album and all associated tracks from the artist's catalog.

        Args:
            artist_id: The artist's ID (auto-bound by AgenticToolManager)
            album_id: The ID of the album to delete

        Returns:
            Dictionary containing the deletion confirmation
        """
        # First verify the album belongs to this artist
        async with AsyncSessionLocal() as session:
            album_result = await session.execute(
                select(Album).where(Album.id == album_id, Album.artist_id == artist_id)
            )
            album = album_result.scalar_one_or_none()

            if not album:
                return {
                    "success": False,
                    "error": "Album not found or doesn't belong to this artist"
                }

            album_title = album.title

            # Use CRUD operations to delete album
            await self.delete(album_id)
            return {
                "success": True,
                "message": f"Album '{album_title}' and all its tracks deleted successfully"
            }

    @tool("album:list")
    async def list_albums(self, artist_id: int) -> Dict[str, Any]:
        """List all albums in the artist's catalog.

        This function retrieves all albums belonging to the artist with their basic information.

        Args:
            artist_id: The artist's ID (auto-bound by AgenticToolManager)

        Returns:
            Dictionary containing the list of albums
        """
        # Get all albums for this artist
        query_params = self._get_owner_filter(artist_id, 'artist_id')
        result = await self.list(query_params)

        # Add artist info
        async with AsyncSessionLocal() as session:
            artist_result = await session.execute(
                select(Artist).where(Artist.id == artist_id)
            )
            artist = artist_result.scalar_one_or_none()

        return {
            "success": True,
            "artist": artist.to_dict() if artist else None,
            "albums": result.get("data", []),
            "total_albums": result.get("pagination", {}).get("total", 0)
        }


# Create an instance for the plugin to use
album_tool_service = AlbumToolService()
