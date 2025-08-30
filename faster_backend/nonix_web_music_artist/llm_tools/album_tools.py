from typing import Dict, Any, List
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from ..models.album import Album
from ..models.track import Track
from ..models.artist import Artist


async def album_list_by_artist(artist_id: int) -> Dict[str, Any]:
    """List all albums for a specific artist with their tracks."""
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
        
        albums_with_tracks = []
        for album in albums:
            tracks_result = await db_session.execute(
                select(Track).where(Track.album_id == album.id)
            )
            tracks = tracks_result.scalars().all()
            
            albums_with_tracks.append({
                "album": album.to_dict(),
                "tracks": [track.to_dict() for track in tracks],
                "track_count": len(tracks)
            })
        
        return {
            "artist": artist.to_dict(),
            "albums": albums_with_tracks,
            "total_albums": len(albums)
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
