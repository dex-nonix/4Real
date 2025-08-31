from typing import Dict, Any, Optional
from datetime import date

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.album import Album
from ..models.track import Track
from ..models.artist import Artist
from ..services.album.album_schemas import AlbumCreate, AlbumUpdate
from ..services.track.track_schemas import TrackCreate, TrackUpdate
from ..services.artist.artist_schemas import ArtistCreate, ArtistUpdate


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


class ArtistToolService(AgenticCrudTools):
    """Artist self-management operations."""

    prefix = "artist"
    config = CRUDConfig(
        model=Artist,
        create_schema=ArtistCreate,
        update_schema=ArtistUpdate,
        response_schema=ArtistCreate,  # Use ArtistCreate as response schema
        filters=FilterConfig(allowed_fields=['name', 'bio', 'genre', 'country']),
        sorting=SortingConfig(default_sort='name', allowed_fields=['name', 'created_at']),
        validation=ValidationConfig(unique_fields=['name'])
    )

    @tool("get_my_info")
    async def get_my_info(self, artist_id: int) -> Dict[str, Any]:
        """Get my own artist information."""
        return await self.get(item_id=artist_id)

    @tool("update_my_info")
    async def update_my_info(self, artist_id: int, name: Optional[str] = None, bio: Optional[str] = None, genre: Optional[str] = None, country: Optional[str] = None) -> Dict[str, Any]:
        """Update my own artist details."""
        return await self.update(
            item_id=artist_id,
            name=name,
            bio=bio,
            genre=genre,
            country=country
        )

    @tool("get_my_discography")
    async def get_my_discography(self, artist_id: int) -> Dict[str, Any]:
        """Get my own discography with albums and tracks."""
        # Get my artist details
        artist_result = await self.get(item_id=artist_id)
        if not artist_result.get("success"):
            return artist_result
        
        # Get my albums
        albums_result = await album_tool_service.list_albums(artist_id)
        
        return {
            "success": True,
            "artist": artist_result.get("data"),
            "albums": albums_result.get("data", []),
            "album_count": len(albums_result.get("data", []))
        }

    @tool("get_my_stats")
    async def get_my_stats(self, artist_id: int) -> Dict[str, Any]:
        """Get my own artist statistics."""
        # Get my artist details
        artist_result = await self.get(item_id=artist_id)
        if not artist_result.get("success"):
            return artist_result
        
        # Get my albums count
        
        albums_result = await album_tool_service.list_albums(artist_id)
        
        # Get my tracks count
        
        tracks_result = await track_tool_service.list_tracks(artist_id)
        
        return {
            "success": True,
            "artist": artist_result.get("data"),
            "stats": {
                "album_count": len(albums_result.get("data", [])),
                "track_count": len(tracks_result.get("data", [])),
                "total_duration": sum(track.get("duration", 0) for track in tracks_result.get("data", []))
            }
        }


# Create instances for the plugin to use
album_tool_service = AlbumToolService()
track_tool_service = TrackToolService()
artist_tool_service = ArtistToolService()
