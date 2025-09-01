from typing import Dict, Any, Optional

from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, PaginationConfig
from ..models.artist import Artist
from ..services.artist.artist_schemas import ArtistCreate, ArtistUpdate


class ArtistToolService(AgenticCrudTools):
    """Artist management operations."""

    prefix = "artist"
    config = CRUDConfig(
        model=Artist,
        create_schema=ArtistCreate,
        update_schema=ArtistUpdate,
        response_schema=ArtistCreate,  # Use ArtistCreate as response schema
        filters=FilterConfig(
            allowed_fields=[],  # Empty = all fields can be filtered
            search_fields=['name', 'bio', 'genre'],  # Fields to search by default
            context_aware=True,
            strict_filtering=False  # Allow filtering on any field
        ),
        sorting=SortingConfig(
            default_sort='name', 
            allowed_fields=['name', 'created_at'],
            strict_sorting=False
        ),
        pagination=PaginationConfig(default_page_size=20, max_page_size=100, min_page_size=5),
        validation=ValidationConfig(unique_fields=['name'])
    )

    @tool("get")
    async def get_artist(self, artist_id: int) -> Dict[str, Any]:
        """Get artist information."""
        return await self.get(item_id=artist_id)

    @tool("update")
    async def update_artist(self, artist_id: int, name: Optional[str] = None, bio: Optional[str] = None,
                            genre: Optional[str] = None, country: Optional[str] = None) -> Dict[str, Any]:
        """Update artist details."""
        return await self.update(
            item_id=artist_id,
            name=name,
            bio=bio,
            genre=genre,
            country=country
        )

    @tool("list")
    async def list_artists(self, filter_value: Optional[str] = None, order_by: Optional[str] = None, page: Optional[int] = None, per_page: Optional[int] = None) -> Dict[str, Any]:
        """List all artists with optional filtering, sorting, and pagination."""
        return await self.list(filter_value=filter_value, order_by=order_by, page=page, per_page=per_page)

    @tool("create")
    async def create_artist(self, name: str, bio: Optional[str] = None, genre: Optional[str] = None,
                            country: Optional[str] = None) -> Dict[str, Any]:
        """Create a new artist."""
        return await self.create(
            name=name,
            bio=bio,
            genre=genre,
            country=country
        )

    @tool("delete")
    async def delete_artist(self, artist_id: int) -> Dict[str, Any]:
        """Delete an artist and all associated content."""
        return await self.delete(item_id=artist_id)

    @tool("catalog")
    async def get_artist_catalog(self, artist_id: int) -> Dict[str, Any]:
        """Get complete artist catalog with albums, tracks, and styles."""
        # Get artist details
        artist_result = await self.get(item_id=artist_id)
        if not artist_result.get("success"):
            return artist_result

        # Get albums with track counts
        from .album_tools import album_tool_service
        albums_result = await album_tool_service.list_albums(artist_id)
        albums = albums_result.get("data", [])

        # Get all tracks
        from .track_tools import track_tool_service
        tracks_result = await track_tool_service.list_tracks(artist_id)
        tracks = tracks_result.get("data", [])

        # Get styles used by this artist
        from .style_tools import style_tool_service
        styles_result = await style_tool_service.list_styles()
        all_styles = styles_result.get("data", [])

        # Count tracks per album
        album_track_counts = {}
        for album in albums:
            album_track_counts[album["id"]] = len([t for t in tracks if t.get("album_id") == album["id"]])

        # Add track counts to albums
        for album in albums:
            album["track_count"] = album_track_counts.get(album["id"], 0)

        return {
            "success": True,
            "artist": artist_result.get("data"),
            "catalog": {
                "albums": albums,
                "tracks": tracks,
                "styles": all_styles,
                "summary": {
                    "album_count": len(albums),
                    "track_count": len(tracks),
                    "style_count": len(all_styles)
                }
            }
        }

    @tool("stats")
    async def get_artist_stats(self, artist_id: int) -> Dict[str, Any]:
        """Get comprehensive artist statistics and analytics."""
        # Get artist details
        artist_result = await self.get(item_id=artist_id)
        if not artist_result.get("success"):
            return artist_result

        # Get albums
        from .album_tools import album_tool_service
        albums_result = await album_tool_service.list_albums(artist_id)
        albums = albums_result.get("data", [])

        # Get tracks
        from .track_tools import track_tool_service
        tracks_result = await track_tool_service.list_tracks(artist_id)
        tracks = tracks_result.get("data", [])

        # Calculate statistics
        total_duration = sum(track.get("duration_seconds", 0) for track in tracks)
        tracks_with_lyrics = len([t for t in tracks if t.get("lyrics")])
        tracks_without_lyrics = len(tracks) - tracks_with_lyrics

        # Album statistics
        album_release_years = {}
        for album in albums:
            if album.get("release_date"):
                year = album["release_date"].year if hasattr(album["release_date"], "year") else album["release_date"][
                                                                                                 :4]
                album_release_years[year] = album_release_years.get(year, 0) + 1

        # Track statistics
        track_titles = [t.get("title", "") for t in tracks]
        avg_title_length = sum(len(title) for title in track_titles) / len(track_titles) if track_titles else 0

        return {
            "success": True,
            "artist": artist_result.get("data"),
            "statistics": {
                "catalog": {
                    "album_count": len(albums),
                    "track_count": len(tracks),
                    "total_duration_seconds": total_duration,
                    "total_duration_formatted": f"{total_duration // 60}:{total_duration % 60:02d}"
                },
                "content": {
                    "tracks_with_lyrics": tracks_with_lyrics,
                    "tracks_without_lyrics": tracks_without_lyrics,
                    "lyrics_coverage_percent": round((tracks_with_lyrics / len(tracks)) * 100, 1) if tracks else 0
                },
                "releases": {
                    "release_years": album_release_years,
                    "most_prolific_year": max(album_release_years.items(), key=lambda x: x[1])[
                        0] if album_release_years else None
                },
                "analytics": {
                    "avg_track_title_length": round(avg_title_length, 1),
                    "longest_track_title": max(track_titles, key=len) if track_titles else None,
                    "shortest_track_title": min(track_titles, key=len) if track_titles else None
                }
            }
        }


# Create an instance for the plugin to use
artist_tool_service = ArtistToolService()
