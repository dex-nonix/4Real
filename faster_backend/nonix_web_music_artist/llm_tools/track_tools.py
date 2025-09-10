from typing import Dict, Any, Optional

from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, PaginationConfig
from ..models.album import Album
from ..models.track import Track
from ..routers.track import TrackCreate, TrackUpdate


class TrackToolService(AgenticCrudTools):
    """Track CRUD operations for artists."""

    prefix = "track"
    config = CRUDConfig(
        model=Track,
        create_schema=TrackCreate,
        update_schema=TrackUpdate,
        response_schema=TrackCreate,  # Use TrackCreate as response schema
        filters=FilterConfig(
            allowed_fields=[],  # Empty = all fields can be filtered
            auto_filters={'artist_id': 'artist_id'},  # Auto-apply artist_id from context
            default_filters={'artist_id': 'required'},  # artist_id is always required
            search_fields=['title', 'lyrics'],  # Fields to search by default
            context_aware=True,
            strict_filtering=False  # Allow filtering on any field
        ),
        sorting=SortingConfig(
            default_sort='title',
            allowed_fields=['title', 'duration', 'created_at', 'artist_id', 'album_id'],
            strict_sorting=False
        ),
        pagination=PaginationConfig(default_page_size=20, max_page_size=100, min_page_size=5),
        validation=ValidationConfig(unique_fields=[])
    )

    @tool("create")
    async def create_track(self, artist_id: int, title: str, album_id: int, duration: Optional[int] = None,
                           lyrics: Optional[str] = None) -> Dict[str, Any]:
        """Create a new track for the artist."""
        return await self.create(
            title=title,
            album_id=album_id,
            artist_id=artist_id,
            duration=duration,
            lyrics=lyrics
        )

    @tool("update")
    async def update_track(self, artist_id: int, track_id: int, title: Optional[str] = None,
                           duration: Optional[int] = None, lyrics: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing track's details."""
        return await self.update(
            item_id=track_id,
            title=title,
            duration=duration,
            lyrics=lyrics
        )

    @tool("delete")
    async def delete_track(self, artist_id: int, track_id: int) -> Dict[str, Any]:
        """Delete a track."""
        return await self.delete(item_id=track_id)

    @tool("get")
    async def get_track(self, artist_id: int, track_id: int) -> Dict[str, Any]:
        """Get details of a single track."""
        return await self.get(item_id=track_id)

    @tool("list")
    async def list_tracks(self, artist_id: int, filter_value: Optional[str] = None, order_by: Optional[str] = None,
                          page: Optional[int] = None, per_page: Optional[int] = None) -> Dict[str, Any]:
        """List all tracks for the artist with optional filtering, sorting, and pagination."""
        return await self.list(context={"artist_id": artist_id}, filter_value=filter_value, order_by=order_by,
                               page=page, per_page=per_page)

    @tool("list_by_album")
    async def list_tracks_by_album(self, artist_id: int, album_id: int, filter_value: Optional[str] = None,
                                   order_by: Optional[str] = None, page: Optional[int] = None,
                                   per_page: Optional[int] = None) -> Dict[str, Any]:
        """List all tracks for a specific album with optional filtering, sorting, and pagination."""
        return await self.list(context={'artist_id': artist_id}, filter_album_id=album_id, filter_value=filter_value,
                               order_by=order_by, page=page, per_page=per_page)

    @tool("move")
    async def move_track(self, artist_id: int, track_id: int, new_album_id: int) -> Dict[str, Any]:
        """Move a track to a different album."""

        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                self.config.model.__table__.select().where(
                    self.config.model.id == track_id,
                    self.config.model.artist_id == artist_id
                )
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Verify new album belongs to artist
            album_result = await session.execute(
                Album.__table__.select().where(Album.id == new_album_id, Album.artist_id == artist_id)
            )
            album = album_result.fetchone()
            if not album:
                return {"success": False, "error": "Album not found or doesn't belong to this artist"}

            # Move track to new album
            await session.execute(
                self.config.model.__table__.update()
                .where(self.config.model.id == track_id)
                .values(album_id=new_album_id)
            )
            await session.commit()

            return {"success": True, "message": f"Track moved to new album"}

    @tool("position")
    async def set_track_position(self, artist_id: int, track_id: int, position: int) -> Dict[str, Any]:
        """Set track position in album."""

        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                self.config.model.__table__.select().where(
                    self.config.model.id == track_id,
                    self.config.model.artist_id == artist_id
                )
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Set track position
            await session.execute(
                self.config.model.__table__.update()
                .where(self.config.model.id == track_id)
                .values(track_number=position)
            )
            await session.commit()

            return {"success": True, "message": f"Track position set to {position}"}

    @tool("bulk_move")
    async def bulk_move_tracks(self, artist_id: int, track_ids: list, new_album_id: int) -> Dict[str, Any]:
        """Move multiple tracks to a different album at once."""

        async with AsyncSessionLocal() as session:
            # Verify new album belongs to artist
            album_result = await session.execute(
                Album.__table__.select().where(Album.id == new_album_id, Album.artist_id == artist_id)
            )
            album = album_result.fetchone()
            if not album:
                return {"success": False, "error": "Album not found or doesn't belong to this artist"}

            # Verify all tracks belong to artist
            tracks_result = await session.execute(
                self.config.model.__table__.select().where(
                    self.config.model.id.in_(track_ids),
                    self.config.model.artist_id == artist_id
                )
            )
            tracks = tracks_result.fetchall()
            if len(tracks) != len(track_ids):
                return {"success": False, "error": "Some tracks not found or don't belong to this artist"}

            # Move all tracks to new album
            await session.execute(
                self.config.model.__table__.update()
                .where(self.config.model.id.in_(track_ids))
                .values(album_id=new_album_id)
            )
            await session.commit()

            return {"success": True, "message": f"Moved {len(track_ids)} tracks to new album"}


# Create an instance for the plugin to use
track_tool_service = TrackToolService()
