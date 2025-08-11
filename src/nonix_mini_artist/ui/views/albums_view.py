"""
Albums view using generic CRUD base class
"""
from ..components.generic_crud_view import GenericCRUDView
from ...services.music_service import MusicService
from ...core.models import Album, Artist

class AlbumsView(GenericCRUDView):
    """Albums view using generic CRUD base class"""
    
    def __init__(self, music_service: MusicService):
        """Initialize albums view with generic configuration"""
        entity_config = {
            'name': 'Album',
            'model': Album,
            'fields': ['album_number', 'title', 'artist', 'release_date'],
            'columns': ['album_number', 'title', 'artist', 'release_date', 'created_at'],
            'crud': music_service.album_crud,
            'icon': '💿',
            'search_placeholder': 'Search albums by title...'
        }
        super().__init__(music_service, entity_config)
        self.artists = []
    
    def _load_data(self):
        """Load albums and artists data"""
        try:
            data = self.music_service.list_albums()
            self.table.update_data(data)
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error loading data: {str(e)}', type='negative')
    
    async def _create_entity(self, **kwargs):
        """Override to handle artist selection logic"""
        try:
            # Handle artist selection
            if 'artist' in kwargs and isinstance(kwargs['artist'], str):
                # Find artist by name
                artist_name = kwargs['artist']
                artist = next((a for a in self.artists if a.name == artist_name), None)
                if artist:
                    kwargs['artist_id'] = artist.id
                    del kwargs['artist']
                else:
                    from nicegui import ui
                    ui.notify('Artist not found. Please select a valid artist.', type='negative')
                    return
            
            # Call parent method
            await super()._create_entity(**kwargs)
            
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error creating album: {str(e)}', type='negative')
    
    async def refresh_data(self):
        """Refresh albums data"""
        try:
            self.items = await self.music_service.list_albums()
            self.filtered_items = self.items.copy()
            self.table.update_data(self.filtered_items)
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error loading albums: {str(e)}', type='negative')
