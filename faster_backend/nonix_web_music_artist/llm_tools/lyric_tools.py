from typing import Dict, Any, Optional

from nonix_web_db import AsyncSessionLocal
from nonix_web_agentic.llm.agentic_tools import AgenticTools, tool
from ..models.track import Track



class LyricToolService(AgenticTools):
    """Lyrics management operations for artists."""

    prefix = "lyric"

    @tool("create_lyrics")
    async def create_lyrics(self, artist_id: int, track_id: int, content: str, language: Optional[str] = "en") -> Dict[str, Any]:
        """Create lyrics for a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Check if lyrics already exist for this track
            if track.lyrics:
                return {"success": False, "error": "Lyrics already exist for this track"}

            # Update track with lyrics
            await session.execute(
                Track.__table__.update()
                .where(Track.id == track_id)
                .values(lyrics=content)
            )
            await session.commit()

            return {
                "success": True,
                "message": f"Lyrics created for track '{track.title}'",
                "lyric": {
                    "track_id": track_id,
                    "content": content,
                    "language": language
                }
            }

    @tool("update_lyrics")
    async def update_lyrics(self, artist_id: int, track_id: int, content: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Update lyrics for a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Check if lyrics exist for this track
            if not track.lyrics:
                return {"success": False, "error": "No lyrics found for this track"}

            # Update lyrics
            await session.execute(
                Track.__table__.update()
                .where(Track.id == track_id)
                .values(lyrics=content)
            )
            await session.commit()

            return {
                "success": True,
                "message": f"Lyrics updated for track '{track.title}'",
                "lyric": {
                    "track_id": track_id,
                    "content": content,
                    "language": language or "en"
                }
            }

    @tool("get_lyrics")
    async def get_lyrics(self, artist_id: int, track_id: int) -> Dict[str, Any]:
        """Get lyrics for a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Check if lyrics exist
            if not track.lyrics:
                return {"success": False, "error": "No lyrics found for this track"}

            return {
                "success": True,
                "track": {"id": track_id, "title": track.title},
                "lyrics": {
                    "content": track.lyrics,
                    "language": "en"
                }
            }

    @tool("delete_lyrics")
    async def delete_lyrics(self, artist_id: int, track_id: int) -> Dict[str, Any]:
        """Delete lyrics for a track."""
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}

            # Check if lyrics exist
            if not track.lyrics:
                return {"success": False, "error": "No lyrics found for this track"}

            # Delete lyrics by setting to None
            await session.execute(
                Track.__table__.update()
                .where(Track.id == track_id)
                .values(lyrics=None)
            )
            await session.commit()

            return {
                "success": True,
                "message": f"Lyrics deleted for track '{track.title}'",
                "track_id": track_id
            }

    @tool("list_tracks_with_lyrics")
    async def list_tracks_with_lyrics(self, artist_id: int) -> Dict[str, Any]:
        """List all tracks by an artist that have lyrics."""
        async with AsyncSessionLocal() as session:
            # Get tracks with lyrics
            tracks_result = await session.execute(
                Track.__table__.select()
                .where(Track.artist_id == artist_id, Track.lyrics.isnot(None))
            )
            tracks = tracks_result.fetchall()

            tracks_with_lyrics = []
            for track in tracks:
                tracks_with_lyrics.append({
                    "track_id": track.id,
                    "title": track.title,
                    "album_id": track.album_id,
                    "lyrics": {
                        "content": track.lyrics,
                        "language": "en",
                        "has_content": bool(track.lyrics)
                    }
                })

            return {
                "success": True,
                "artist_id": artist_id,
                "tracks_with_lyrics": tracks_with_lyrics,
                "total_tracks": len(tracks_with_lyrics)
            }

    @tool("search_lyrics")
    async def search_lyrics(self, artist_id: int, query: str) -> Dict[str, Any]:
        """Search lyrics content across artist's tracks."""
        async with AsyncSessionLocal() as session:
            # Search lyrics content directly in Track table
            search_result = await session.execute(
                Track.__table__.select()
                .where(
                    Track.artist_id == artist_id,
                    Track.lyrics.isnot(None),
                    Track.lyrics.ilike(f"%{query}%")
                )
            )
            results = search_result.fetchall()

            search_results = []
            for track in results:
                search_results.append({
                    "track_id": track.id,
                    "track_title": track.title,
                    "content_preview": track.lyrics[:100] + "..." if len(track.lyrics) > 100 else track.lyrics,
                    "language": "en"
                })

            return {
                "success": True,
                "query": query,
                "artist_id": artist_id,
                "search_results": search_results,
                "total_results": len(search_results)
            }


# Create an instance for the plugin to use
lyric_tool_service = LyricToolService()
