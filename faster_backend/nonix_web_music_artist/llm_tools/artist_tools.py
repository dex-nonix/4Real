from datetime import date
from typing import Dict, Any, Optional

from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, PaginationConfig
from ..models.artist import Artist
from ..routers.artist.artist_schemas import ArtistCreate, ArtistUpdate, ArtistInDbModel


class ArtistToolService(AgenticCrudTools):
    """Artist management operations."""

    prefix = "artist"
    config = CRUDConfig(
        model=Artist,
        create_schema=ArtistCreate,
        update_schema=ArtistUpdate,
        response_schema=ArtistInDbModel,
        filters=FilterConfig(
            allowed_fields=[],
            search_fields=['name', 'abbreviation', 'persona'],
            context_aware=True,
            strict_filtering=False
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
    async def update_artist(self, artist_id: int, name: Optional[str] = None, abbreviation: Optional[str] = None,
                            persona: Optional[str] = None, birth_date: Optional[date] = None) -> Dict[str, Any]:
        update_data: Dict[str, Any] = {}
        if name is not None:
            update_data['name'] = name
        if abbreviation is not None:
            update_data['abbreviation'] = abbreviation
        if persona is not None:
            update_data['persona'] = persona
        if birth_date is not None:
            update_data['birth_date'] = birth_date
        return await self.update(item_id=artist_id, **update_data)

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
