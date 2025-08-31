from typing import Dict, Any, Optional

from nonix_web_db import AsyncSessionLocal
from nonix_web_agentic.llm.agentic_tools import AgenticTools, tool
from ..models.track import Track
from ..models.lyric import Lyric


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
            existing_result = await session.execute(
                Lyric.__table__.select().where(Lyric.track_id == track_id)
            )
            if existing_result.fetchone():
                return {"success": False, "error": "Lyrics already exist for this track"}

            # Create lyrics
            lyric = Lyric(
                track_id=track_id,
                content=content,
                language=language
            )
            session.add(lyric)
            await session.commit()
            await session.refresh(lyric)

            return {
                "success": True,
                "message": f"Lyrics created for track '{track.title}'",
                "lyric": {
                    "id": lyric.id,
                    "track_id": track_id,
                    "content": lyric.content,
                    "language": lyric.language,
                    "created_at": lyric.created_at.isoformat() if lyric.created_at else None
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

            # Get existing lyrics
            lyric_result = await session.execute(
                Lyric.__table__.select().where(Lyric.track_id == track_id)
            )
            lyric = lyric_result.fetchone()
            if not lyric:
                return {"success": False, "error": "No lyrics found for this track"}

            # Update lyrics
            update_data = {"content": content}
            if language:
                update_data["language"] = language

            await session.execute(
                Lyric.__table__.update()
                .where(Lyric.track_id == track_id)
                .values(**update_data)
            )
            await session.commit()

            return {
                "success": True,
                "message": f"Lyrics updated for track '{track.title}'",
                "lyric": {
                    "track_id": track_id,
                    "content": content,
                    "language": language or lyric.language,
                    "updated_at": "now"
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

            # Get lyrics
            lyric_result = await session.execute(
                Lyric.__table__.select().where(Lyric.track_id == track_id)
            )
            lyric = lyric_result.fetchone()
            if not lyric:
                return {"success": False, "error": "No lyrics found for this track"}

            return {
                "success": True,
                "track": {"id": track_id, "title": track.title},
                "lyrics": {
                    "id": lyric.id,
                    "content": lyric.content,
                    "language": lyric.language,
                    "created_at": lyric.created_at.isoformat() if lyric.created_at else None,
                    "updated_at": lyric.updated_at.isoformat() if lyric.updated_at else None
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

            # Delete lyrics
            delete_result = await session.execute(
                Lyric.__table__.delete().where(Lyric.track_id == track_id)
            )
            await session.commit()

            if delete_result.rowcount == 0:
                return {"success": False, "error": "No lyrics found for this track"}

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
                .join(Lyric, Track.id == Lyric.track_id)
                .where(Track.artist_id == artist_id)
                .distinct()
            )
            tracks = tracks_result.fetchall()

            tracks_with_lyrics = []
            for track in tracks:
                # Get lyrics for this track
                lyric_result = await session.execute(
                    Lyric.__table__.select().where(Lyric.track_id == track.id)
                )
                lyric = lyric_result.fetchone()
                
                tracks_with_lyrics.append({
                    "track_id": track.id,
                    "title": track.title,
                    "album_id": track.album_id,
                    "lyrics": {
                        "id": lyric.id,
                        "language": lyric.language,
                        "has_content": bool(lyric.content)
                    } if lyric else None
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
            # Search lyrics content
            search_result = await session.execute(
                Lyric.__table__.select()
                .join(Track, Lyric.track_id == Track.id)
                .where(
                    Track.artist_id == artist_id,
                    Lyric.content.ilike(f"%{query}%")
                )
            )
            results = search_result.fetchall()

            search_results = []
            for lyric in results:
                # Get track info
                track_result = await session.execute(
                    Track.__table__.select().where(Track.id == lyric.track_id)
                )
                track = track_result.fetchone()
                
                search_results.append({
                    "track_id": track.id,
                    "track_title": track.title,
                    "lyric_id": lyric.id,
                    "content_preview": lyric.content[:100] + "..." if len(lyric.content) > 100 else lyric.content,
                    "language": lyric.language
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
