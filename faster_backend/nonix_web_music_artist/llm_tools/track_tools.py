from typing import Dict, Any, Optional

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.track import Track
from ..services.track.track_schemas import TrackCreate, TrackUpdate


class TrackToolService(AgenticCrudTools):
    """Track CRUD operations for artists."""

    prefix = "track"
    config = CRUDConfig(
        model=Track,
        create_schema=TrackCreate,
        update_schema=TrackUpdate,
        response_schema=TrackCreate,  # Use TrackCreate as response schema
        filters=FilterConfig(allowed_fields=['title', 'duration', 'album_id', 'artist_id']),
        sorting=SortingConfig(default_sort='title', allowed_fields=['title', 'duration', 'created_at']),
        validation=ValidationConfig(unique_fields=[])
    )

    @tool("create")
    async def create_track(self, artist_id: int, title: str, album_id: int, duration: Optional[int] = None, lyrics: Optional[str] = None) -> Dict[str, Any]:
        """Create a new track for the artist."""
        return await self.create(
            title=title,
            album_id=album_id,
            artist_id=artist_id,
            duration=duration,
            lyrics=lyrics
        )

    @tool("update")
    async def update_track(self, artist_id: int, track_id: int, title: Optional[str] = None, duration: Optional[int] = None, lyrics: Optional[str] = None) -> Dict[str, Any]:
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
    async def list_tracks(self, artist_id: int) -> Dict[str, Any]:
        """List all tracks for the artist."""
        return await self.list(filters=[self.config.model.artist_id == artist_id])

    @tool("list_by_album")
    async def list_tracks_by_album(self, artist_id: int, album_id: int) -> Dict[str, Any]:
        """List all tracks for a specific album."""
        return await self.list(filters=[
            self.config.model.album_id == album_id,
            self.config.model.artist_id == artist_id
        ])


# Create an instance for the plugin to use
track_tool_service = TrackToolService()
