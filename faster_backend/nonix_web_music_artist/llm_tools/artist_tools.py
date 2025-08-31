from typing import Dict, Any, Optional

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.artist import Artist
from ..services.artist.artist_schemas import ArtistCreate, ArtistUpdate


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
        from .album_tools import album_tool_service
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
        from .album_tools import album_tool_service
        albums_result = await album_tool_service.list_albums(artist_id)
        
        # Get my tracks count
        from .track_tools import track_tool_service
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


# Create an instance for the plugin to use
artist_tool_service = ArtistToolService()
