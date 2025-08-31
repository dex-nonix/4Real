from typing import Dict, Any, List

from nonix_web_db import AsyncSessionLocal
from nonix_web_agentic.llm.agentic_tools import AgenticTools, tool
from ..models.track import Track
from ..models.style import Style
from ..models.associations import TrackStyle


class TrackStyleToolService(AgenticTools):
    """Track-Style relationship management for artists."""

    prefix = "track_style"

    @tool("add_style_to_track")
    async def add_style_to_track(self, artist_id: int, track_id: int, style_id: int) -> Dict[str, Any]:
        """Add a style to a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Verify style exists
            style_result = await session.execute(
                Style.__table__.select().where(Style.id == style_id)
            )
            style = style_result.fetchone()
            if not style:
                return {"success": False, "error": "Style not found"}

            # Check if relationship already exists
            existing_result = await session.execute(
                TrackStyle.__table__.select().where(
                    TrackStyle.track_id == track_id, 
                    TrackStyle.style_id == style_id
                )
            )
            if existing_result.fetchone():
                return {"success": False, "error": "Style already assigned to this track"}

            # Create relationship
            track_style = TrackStyle(track_id=track_id, style_id=style_id)
            session.add(track_style)
            await session.commit()

            return {
                "success": True,
                "message": f"Style '{style.name}' added to track '{track.title}'",
                "track_style": {"track_id": track_id, "style_id": style_id}
            }

    @tool("remove_style_from_track")
    async def remove_style_from_track(self, artist_id: int, track_id: int, style_id: int) -> Dict[str, Any]:
        """Remove a style from a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Remove relationship
            delete_result = await session.execute(
                TrackStyle.__table__.delete().where(
                    TrackStyle.track_id == track_id, 
                    TrackStyle.style_id == style_id
                )
            )
            await session.commit()

            if delete_result.rowcount == 0:
                return {"success": False, "error": "Style was not assigned to this track"}

            return {
                "success": True,
                "message": f"Style removed from track '{track.title}'",
                "track_style": {"track_id": track_id, "style_id": style_id}
            }

    @tool("list_track_styles")
    async def list_track_styles(self, artist_id: int, track_id: int) -> Dict[str, Any]:
        """List all styles assigned to a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Get styles for this track
            styles_result = await session.execute(
                Style.__table__.select()
                .join(TrackStyle, Style.id == TrackStyle.style_id)
                .where(TrackStyle.track_id == track_id)
            )
            styles = styles_result.fetchall()

            return {
                "success": True,
                "track": {"id": track_id, "title": track.title},
                "styles": [{"id": style.id, "name": style.name, "category": style.category} for style in styles],
                "style_count": len(styles)
            }

    @tool("list_artist_styles")
    async def list_artist_styles(self, artist_id: int) -> Dict[str, Any]:
        """List all styles used by an artist across all tracks."""
        async with AsyncSessionLocal() as session:
            # Get all styles used by artist's tracks
            styles_result = await session.execute(
                Style.__table__.select()
                .join(TrackStyle, Style.id == TrackStyle.style_id)
                .join(Track, TrackStyle.track_id == Track.id)
                .where(Track.artist_id == artist_id)
                .distinct()
            )
            styles = styles_result.fetchall()

            # Count usage for each style
            style_usage = []
            for style in styles:
                usage_result = await session.execute(
                    TrackStyle.__table__.select()
                    .join(Track, TrackStyle.track_id == Track.id)
                    .where(Track.artist_id == artist_id, TrackStyle.style_id == style.id)
                )
                usage_count = len(usage_result.fetchall())
                style_usage.append({
                    "id": style.id,
                    "name": style.name,
                    "category": style.category,
                    "usage_count": usage_count
                })

            return {
                "success": True,
                "artist_id": artist_id,
                "styles": style_usage,
                "total_styles": len(styles)
            }

    @tool("get_tracks_by_style")
    async def get_tracks_by_style(self, artist_id: int, style_id: int) -> Dict[str, Any]:
        """Get all tracks by an artist that use a specific style."""
        async with AsyncSessionLocal() as session:
            # Verify style exists
            style_result = await session.execute(
                Style.__table__.select().where(Style.id == style_id)
            )
            style = style_result.fetchone()
            if not style:
                return {"success": False, "error": "Style not found"}

            # Get tracks using this style
            tracks_result = await session.execute(
                Track.__table__.select()
                .join(TrackStyle, Track.id == TrackStyle.track_id)
                .where(Track.artist_id == artist_id, TrackStyle.style_id == style_id)
            )
            tracks = tracks_result.fetchall()

            return {
                "success": True,
                "style": {"id": style.id, "name": style.name, "category": style.category},
                "tracks": [{"id": track.id, "title": track.title, "album_id": track.album_id} for track in tracks],
                "track_count": len(tracks)
            }


# Create an instance for the plugin to use
track_style_tool_service = TrackStyleToolService()
