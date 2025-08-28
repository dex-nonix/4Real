from typing import Dict, Any, List
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from ..models.artist import Artist
from ..models.album import Album


async def artist_get_info(artist_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific artist."""
    async with AsyncSessionLocal() as db_session:
        artist_result = await db_session.execute(
            select(Artist).where(Artist.id == artist_id)
        )
        artist = artist_result.scalar_one_or_none()
        
        if not artist:
            return {"error": "Artist not found"}
        
        albums_result = await db_session.execute(
            select(Album).where(Album.artist_id == artist_id)
        )
        albums = albums_result.scalars().all()
        
        total_result = await db_session.execute(
            select(Album).where(Album.artist_id == artist_id)
        )
        total = len(total_result.scalars().all())
        
        return {
            "artist": artist.to_dict(),
            "albums": [album.to_dict() for album in albums],
            "album_count": total
        }


async def artist_list_albums(artist_id: int) -> Dict[str, Any]:
    """List all albums for a specific artist with basic info."""
    async with AsyncSessionLocal() as db_session:
        artist_result = await db_session.execute(
            select(Artist).where(Artist.id == artist_id)
        )
        artist = artist_result.scalar_one_or_none()
        
        if not artist:
            return {"error": "Artist not found"}
        
        album_count_result = await db_session.execute(
            select(Album).where(Album.artist_id == artist_id)
        )
        album_count = len(album_count_result.scalars().all())
        
        return {
            "artist": artist.to_dict(),
            "album_count": album_count,
            "message": f"Found {album_count} albums for {artist.name}"
        }
