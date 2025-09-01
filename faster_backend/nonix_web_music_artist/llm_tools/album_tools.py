from datetime import date
from typing import Dict, Any, Optional

from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, PaginationConfig
from ..models.album import Album
from ..models.track import Track
from ..services.album.album_schemas import AlbumCreate, AlbumUpdate


class AlbumToolService(AgenticCrudTools):
    """Album CRUD operations for artists."""

    prefix = "album"
    config = CRUDConfig(
        model=Album,
        create_schema=AlbumCreate,
        update_schema=AlbumUpdate,
        response_schema=AlbumCreate,  # Use AlbumCreate as response schema
        filters=FilterConfig(
            allowed_fields=[],  # Empty = all fields can be filtered
            auto_filters={'artist_id': 'artist_id'},  # Auto-apply artist_id from context
            default_filters={'artist_id': 'required'},  # artist_id is always required
            search_fields=['title', 'description'],  # Fields to search by default
            context_aware=True,
            strict_filtering=False  # Allow filtering on any field
        ),
        sorting=SortingConfig(
            default_sort='release_date', 
            allowed_fields=['title', 'release_date', 'created_at', 'artist_id'],
            strict_sorting=False
        ),
        pagination=PaginationConfig(default_page_size=20, max_page_size=100, min_page_size=5),
        validation=ValidationConfig(unique_fields=[])
    )

    @tool("create")
    async def create_album(self, artist_id: int, title: str, release_date: Optional[date] = None,
                           description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new album for the artist."""
        return await self.create(
            title=title,
            artist_id=artist_id,
            release_date=release_date,
            description=description
        )

    @tool("update")
    async def update_album(self, artist_id: int, album_id: int, title: Optional[str] = None,
                           description: Optional[str] = None) -> Dict[str, Any]:
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
    async def list_albums(self, artist_id: int, filter_value: Optional[str] = None, order_by: Optional[str] = None, page: Optional[int] = None, per_page: Optional[int] = None) -> Dict[str, Any]:
        """List all albums in the artist's catalog with optional filtering, sorting, and pagination."""
        return await self.list(context={"artist_id": artist_id}, filter_value=filter_value, order_by=order_by, page=page, per_page=per_page)

    @tool("add_track")
    async def add_track_to_album(self, artist_id: int, album_id: int, track_id: int) -> Dict[str, Any]:
        """Add a track to an album."""

        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Update track's album_id
            await session.execute(
                Track.__table__.update()
                .where(Track.id == track_id)
                .values(album_id=album_id)
            )
            await session.commit()

            return {"success": True, "message": f"Track added to album"}

    @tool("remove_track")
    async def remove_track_from_album(self, artist_id: int, album_id: int, track_id: int) -> Dict[str, Any]:
        """Remove a track from an album."""

        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist and album
            track_result = await session.execute(
                Track.__table__.select().where(
                    Track.id == track_id,
                    Track.artist_id == artist_id,
                    Track.album_id == album_id
                )
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this album"}

            # Remove track from album by setting album_id to None
            await session.execute(
                Track.__table__.update()
                .where(Track.id == track_id)
                .values(album_id=None)
            )
            await session.commit()

            return {"success": True, "message": f"Track removed from album"}

    @tool("reorder")
    async def reorder_album_tracks(self, artist_id: int, album_id: int, track_order: list) -> Dict[str, Any]:
        """Reorder tracks in an album."""

        async with AsyncSessionLocal() as session:
            # Verify album belongs to artist
            album_result = await session.execute(
                Album.__table__.select().where(Album.id == album_id, Album.artist_id == artist_id)
            )
            album = album_result.fetchone()
            if not album:
                return {"success": False, "error": "Album not found or doesn't belong to this artist"}

            # Update track numbers
            for position, track_id in enumerate(track_order, 1):
                await session.execute(
                    Track.__table__.update()
                    .where(Track.id == track_id, Track.album_id == album_id)
                    .values(track_number=position)
                )

            await session.commit()
            return {"success": True, "message": f"Album track order updated"}

    @tool("bulk_reorder")
    async def bulk_reorder_album_tracks(self, artist_id: int, album_id: int, track_orders: list) -> Dict[str, Any]:
        """Bulk reorder tracks in an album with position updates."""

        async with AsyncSessionLocal() as session:
            # Verify album belongs to artist
            album_result = await session.execute(
                Album.__table__.select().where(Album.id == album_id, Album.artist_id == artist_id)
            )
            album = album_result.fetchone()
            if not album:
                return {"success": False, "error": "Album not found or doesn't belong to this artist"}

            # Verify all tracks belong to artist and album
            track_ids = [order["track_id"] for order in track_orders]
            tracks_result = await session.execute(
                Track.__table__.select().where(
                    Track.id.in_(track_ids),
                    Track.artist_id == artist_id,
                    Track.album_id == album_id
                )
            )
            tracks = tracks_result.fetchall()
            if len(tracks) != len(track_ids):
                return {"success": False, "error": "Some tracks not found or don't belong to this album"}

            # Update track positions
            for order in track_orders:
                await session.execute(
                    Track.__table__.update()
                    .where(Track.id == order["track_id"])
                    .values(track_number=order["position"])
                )

            await session.commit()
            return {"success": True, "message": f"Updated positions for {len(track_orders)} tracks"}


# Create an instance for the plugin to use
album_tool_service = AlbumToolService()
