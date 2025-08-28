from typing import Dict, Any

from ...models.album import Album
from ...models.artist import Artist
from ...models.style import Style
from ...models.track import Track


async def track_list_by_album(album_id: int) -> Dict[str, Any]:
    """List tracks in an album with detailed information."""
    try:
        # Verify album exists
        album = Album.query.filter_by(id=album_id).first()
        if not album:
            return {'status': 'error', 'error': f'Album {album_id} not found'}

        # Get tracks ordered by track number
        tracks = Track.query.filter_by(album_id=album_id) \
            .order_by(Track.track_number.asc()) \
            .all()

        # Get artist info
        artist = Artist.query.filter_by(id=album.artist_id).first()

        return {
            'status': 'success',
            'result': {
                'album': album.to_dict(),
                'artist': artist.to_dict() if artist else None,
                'tracks': [track.to_dict() for track in tracks],
                'track_count': len(tracks),
                'total_duration': sum(track.duration_seconds or 0 for track in tracks)
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}


async def style_list_all() -> Dict[str, Any]:
    """List all music styles."""
    try:
        # Get all styles ordered by name
        styles = Style.query.order_by(Style.name.asc()).all()

        # Get count of artists per style
        style_stats = []
        for style in styles:
            artist_count = Artist.query.filter_by(style_id=style.id).count()
            style_stats.append({
                'style': style.to_dict(),
                'artist_count': artist_count
            })

        return {
            'status': 'success',
            'result': {
                'styles': style_stats,
                'total_styles': len(styles),
                'total_artists': sum(stat['artist_count'] for stat in style_stats)
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}


async def track_get_info(track_id: int) -> Dict[str, Any]:
    """Get detailed track information."""
    try:
        # Get track with related data
        track = Track.query.filter_by(id=track_id).first()
        if not track:
            return {'status': 'error', 'error': f'Track {track_id} not found'}

        # Get album and artist info
        album = Album.query.filter_by(id=track.album_id).first()
        artist = None
        if album:
            artist = Artist.query.filter_by(id=album.artist_id).first()

        return {
            'status': 'success',
            'result': {
                'track': track.to_dict(),
                'album': album.to_dict() if album else None,
                'artist': artist.to_dict() if artist else None
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}
