from typing import Dict, Any

from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from ..models.album import Album
from ..models.artist import Artist
from ..models.style import Style
from ..models.track import Track


async def track_list_by_album(album_id: int) -> Dict[str, Any]:
    """List all tracks for a specific album."""
    async with AsyncSessionLocal() as db_session:
        album_result = await db_session.execute(
            select(Album).where(Album.id == album_id)
        )
        album = album_result.scalar_one_or_none()

        if not album:
            return {"error": "Album not found"}

        tracks_result = await db_session.execute(
            select(Track).where(Track.album_id == album_id)
        )
        tracks = tracks_result.scalars().all()

        artist_result = await db_session.execute(
            select(Artist).where(Artist.id == album.artist_id)
        )
        artist = artist_result.scalar_one_or_none()

        return {
            "album": album.to_dict(),
            "tracks": [track.to_dict() for track in tracks],
            "artist": artist.to_dict() if artist else None,
            "track_count": len(tracks)
        }


async def style_list_all() -> Dict[str, Any]:
    """List all available music styles with artist counts."""
    async with AsyncSessionLocal() as db_session:
        styles_result = await db_session.execute(
            select(Style).order_by(Style.name.asc())
        )
        styles = styles_result.scalars().all()

        style_data = []
        for style in styles:
            artist_count_result = await db_session.execute(
                select(Artist).where(Artist.style_id == style.id)
            )
            artist_count = len(artist_count_result.scalars().all())

            style_data.append({
                "style": style.to_dict(),
                "artist_count": artist_count
            })

        return {
            "styles": style_data,
            "total_styles": len(styles)
        }


async def track_get_info(track_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific track."""
    async with AsyncSessionLocal() as db_session:
        track_result = await db_session.execute(
            select(Track).where(Track.id == track_id)
        )
        track = track_result.scalar_one_or_none()

        if not track:
            return {"error": "Track not found"}

        album_result = await db_session.execute(
            select(Album).where(Album.id == track.album_id)
        )
        album = album_result.scalar_one_or_none()

        artist_result = await db_session.execute(
            select(Artist).where(Artist.id == album.artist_id)
        )
        artist = artist_result.scalar_one_or_none()

        return {
            "track": track.to_dict(),
            "album": album.to_dict() if album else None,
            "artist": artist.to_dict() if artist else None
        }
