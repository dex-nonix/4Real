from typing import Dict, Any, List
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from ..models.album import Album
from ..models.track import Track
from ..models.artist import Artist


async def artist_list_albums(artist_id: int) -> Dict[str, Any]:
    """List all albums for a specific artist."""
    async with AsyncSessionLocal() as db_session:
        album_result = await db_session.execute(
            select(Album).where(Album.id == artist_id)
        )
        album = album_result.scalar_one_or_none()
        
        if not album:
            return {"error": "Album not found"}
        
        tracks_result = await db_session.execute(
            select(Track).where(Track.album_id == artist_id)
        )
        tracks = tracks_result.scalars().all()
        
        return {
            "album": album.to_dict(),
            "tracks": [track.to_dict() for track in tracks]
        }


async def album_get_info(album_id: int) -> Dict[str, Any]:
    """Get detailed information about an album."""
    async with AsyncSessionLocal() as db_session:
        album_result = await db_session.execute(
            select(Album).where(Album.id == album_id)
        )
        album = album_result.scalar_one_or_none()
        
        if not album:
            return {"error": "Album not found"}
        
        artist_result = await db_session.execute(
            select(Artist).where(Artist.id == album.artist_id)
        )
        artist = artist_result.scalar_one_or_none()
        
        track_count_result = await db_session.execute(
            select(Track).where(Track.album_id == album_id)
        )
        track_count = len(track_count_result.scalars().all())
        
        return {
            "album": album.to_dict(),
            "artist": artist.to_dict() if artist else None,
            "track_count": track_count
        }
