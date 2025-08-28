from typing import Dict, Any

from ...models.album import Album
from ...models.artist import Artist


async def artist_list_albums(artist_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """List albums for an artist with pagination."""
    try:
        # Verify artist exists
        artist = Artist.query.filter_by(id=artist_id).first()
        if not artist:
            return {'status': 'error', 'error': f'Artist {artist_id} not found'}

        # Query albums with pagination
        offset = (page - 1) * page_size
        albums = Album.query.filter_by(artist_id=artist_id) \
            .order_by(Album.release_date.desc()) \
            .offset(offset).limit(page_size).all()

        total = Album.query.filter_by(artist_id=artist_id).count()

        return {
            'status': 'success',
            'result': {
                'artist': artist.to_dict(),
                'albums': [album.to_dict() for album in albums],
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'pages': (total + page_size - 1) // page_size
                }
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}


async def artist_get_info(artist_id: int) -> Dict[str, Any]:
    """Get artist details and metadata."""
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        if not artist:
            return {'status': 'error', 'error': f'Artist {artist_id} not found'}

        # Get related data
        album_count = Album.query.filter_by(artist_id=artist_id).count()

        return {
            'status': 'success',
            'result': {
                'artist': artist.to_dict(),
                'stats': {
                    'album_count': album_count
                }
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}
