"""
Styles view using generic CRUD base class
"""
from ..components.generic_crud_view import GenericCRUDView
from ...services.music_service import MusicService
from ...core.models import Style

class StylesView(GenericCRUDView):
    """Styles view using generic CRUD base class"""
    
    def __init__(self, music_service: MusicService):
        """Initialize styles view with generic configuration"""
        entity_config = {
            'name': 'Style',
            'model': Style,
            'fields': ['name', 'category', 'description'],
            'columns': ['name', 'category', 'description', 'created_at'],
            'crud': music_service.style_crud,
            'icon': '🏷️',
            'search_placeholder': 'Search styles by name...'
        }
        super().__init__(music_service, entity_config)
    
    def _load_data(self):
        """Load styles data"""
        try:
            data = self.music_service.list_styles()
            self.table.update_data(data)
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error loading data: {str(e)}', type='negative')
    
    async def refresh_data(self):
        """Refresh styles data"""
        try:
            self.items = await self.music_service.list_styles()
            self.filtered_items = self.items.copy()
            self.table.update_data(self.filtered_items)
        except Exception as e:
            from nicegui import ui
            ui.notify(f'Error loading styles: {str(e)}', type='negative')
