from typing import Dict, Any
from ... import db
from ...models.album import Album
from ...models.track import Track
from ...models.artist import Artist


def album_list_tracks(album_id: int) -> Dict[str, Any]:
    """List tracks in an album."""
    try:
        # Verify album exists
        album = Album.query.filter_by(id=album_id).first()
        if not album:
            return {'status': 'error', 'error': f'Album {album_id} not found'}
        
        # Get tracks ordered by track number
        tracks = Track.query.filter_by(album_id=album_id)\
                          .order_by(Track.track_number.asc())\
                          .all()
        
        return {
            'status': 'success',
            'result': {
                'album': album.to_dict(),
                'tracks': [track.to_dict() for track in tracks],
                'track_count': len(tracks)
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}


def album_get_info(album_id: int) -> Dict[str, Any]:
    """Get album details and metadata."""
    try:
        album = Album.query.filter_by(id=album_id).first()
        if not album:
            return {'status': 'error', 'error': f'Album {album_id} not found'}
        
        # Get related data
        artist = Artist.query.filter_by(id=album.artist_id).first()
        track_count = Track.query.filter_by(album_id=album_id).count()
        
        return {
            'status': 'success',
            'result': {
                'album': album.to_dict(),
                'artist': artist.to_dict() if artist else None,
                'stats': {
                    'track_count': track_count
                }
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}
