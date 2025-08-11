"""
Artists view using generic CRUD base class
"""
from ..components.generic_crud_view import GenericCRUDView
from ...services.music_service import MusicService
from ...core.models import Artist

class ArtistsView(GenericCRUDView):
    """Artists view using generic CRUD base class"""
    
    def __init__(self, music_service: MusicService):
        """Initialize artists view with generic configuration"""
        entity_config = {
            'name': 'Artist',
            'model': Artist,
            'fields': ['name', 'abbreviation', 'persona'],
            'columns': ['name', 'abbreviation', 'created_at'],
            'crud': music_service.artist_crud,
            'icon': '🎤',
            'search_placeholder': 'Search artists by name...'
        }
        super().__init__(music_service, entity_config)
    
    async def _load_data(self):
        """Load artists data"""
        try:
            data = await self.music_service.list_artists()
            self.items = data
            self.filtered_items = data.copy()
            self.table.update_data(data)
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error loading artists: {str(e)}', type='negative')
    
    async def refresh_data(self):
        """Refresh artists data"""
        try:
            self.items = await self.music_service.list_artists()
            self.filtered_items = self.items.copy()
            self.table.update_data(self.filtered_items)
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error loading artists: {str(e)}', type='negative')
