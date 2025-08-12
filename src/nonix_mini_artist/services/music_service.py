"""
Music service using generic CRUD helper
"""
from typing import List, Optional, Dict, Any
from ..crud.helper import CRUDHelper
from ..core.models import Artist, Album, Track, Style
from ..core.database import get_database

class MusicService:
    """Music metadata service using generic CRUD"""
    
    def __init__(self):
        """Initialize CRUD helpers for all entities"""
        self.artist_crud = CRUDHelper(Artist)
        self.album_crud = CRUDHelper(Album)
        self.track_crud = CRUDHelper(Track)
        self.style_crud = CRUDHelper(Style)
        self.db = get_database()
    
    # Artist operations
    def create_artist(self, **kwargs) -> Artist:
        """Create a new artist"""
        return self.artist_crud.create(**kwargs)
    
    def get_artist(self, artist_id: int) -> Optional[Artist]:
        """Get artist by ID"""
        return self.artist_crud.get_by_id(artist_id)
    
    def list_artists(self) -> List[Artist]:
        """List all artists"""
        return self.artist_crud.list_all()
    
    def update_artist(self, artist_id: int, **kwargs) -> Optional[Artist]:
        """Update artist"""
        return self.artist_crud.update(artist_id, **kwargs)
    
    def delete_artist(self, artist_id: int) -> bool:
        """Delete artist"""
        return self.artist_crud.delete(artist_id)
    
    # Album operations
    def create_album(self, **kwargs) -> Album:
        """Create a new album"""
        return self.album_crud.create(**kwargs)
    
    def get_album(self, album_id: int) -> Optional[Album]:
        """Get album by ID"""
        return self.album_crud.get_by_id(album_id)
    
    def list_albums(self, artist_id: Optional[int] = None) -> List[Album]:
        """List albums, optionally filtered by artist"""
        if artist_id:
            return self.album_crud.search(artist_id=artist_id)
        return self.album_crud.list_all()
    
    def update_album(self, album_id: int, **kwargs) -> Optional[Album]:
        """Update album"""
        return self.album_crud.update(album_id, **kwargs)
    
    def delete_album(self, album_id: int) -> bool:
        """Delete album"""
        return self.album_crud.delete(album_id)
    
    # Track operations
    def create_track(self, **kwargs) -> Track:
        """Create a new track"""
        return self.track_crud.create(**kwargs)
    
    def get_track(self, track_id: int) -> Optional[Track]:
        """Get track by ID"""
        return self.track_crud.get_by_id(track_id)
    
    def list_tracks(self, album_id: Optional[int] = None) -> List[Track]:
        """List tracks, optionally filtered by album"""
        if album_id:
            return self.track_crud.search(album_id=album_id)
        return self.track_crud.list_all()
    
    def update_track(self, track_id: int, **kwargs) -> Optional[Track]:
        """Update track"""
        return self.track_crud.update(track_id, **kwargs)
    
    def delete_track(self, track_id: int) -> bool:
        """Delete track"""
        return self.track_crud.delete(track_id)
    
    # Style operations
    def create_style(self, **kwargs) -> Style:
        """Create a new style"""
        return self.style_crud.create(**kwargs)
    
    def list_styles(self) -> List[Style]:
        """List all styles"""
        return self.style_crud.list_all()
    
    # Utility methods
    def get_artist_with_albums(self, artist_id: int) -> Optional[Dict[str, Any]]:
        """Get artist with all albums and tracks"""
        artist = self.get_artist(artist_id)
        if not artist:
            return None
        
        albums = self.list_albums(artist_id=artist_id)
        result = {
            'artist': artist,
            'albums': []
        }
        
        for album in albums:
            tracks = self.list_tracks(album_id=album.id)
            result['albums'].append({
                'album': album,
                'tracks': tracks
            })
        
        return result
    
    def search_music(self, query: str) -> Dict[str, List]:
        """Search across all music entities"""
        # Simple search implementation
        artists = self.artist_crud.search(name__icontains=query)
        albums = self.album_crud.search(title__icontains=query)
        tracks = self.track_crud.search(name__icontains=query)
        
        return {
            'artists': artists,
            'albums': albums,
            'tracks': tracks
        }
