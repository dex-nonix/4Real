"""
Artists view using reusable components
"""
from nicegui import ui
from ..components.generic_table import GenericTable
from ..components.generic_form import GenericForm
from ..components.search_bar import EntitySearchBar
from ...services.music_service import MusicService
from ...core.models import Artist

class ArtistsView:
    """Artists view using reusable components"""
    
    def __init__(self, music_service: MusicService):
        """Initialize artists view"""
        self.music_service = music_service
        self.artists = []
        self.filtered_artists = []
        self._build_view()
    
    def _build_view(self):
        """Build the artists view"""
        with ui.column().classes('w-full') as container:
            self.container = container
            # Header
            ui.label('🎤 Artists').classes('text-3xl font-bold mb-6')
            
            # Search bar
            self.search_bar = EntitySearchBar(
                entity_type="artists",
                on_search=self._handle_search,
                placeholder="Search artists by name..."
            )
            
            # Add new artist button
            ui.button('➕ Add New Artist', on_click=self._show_add_form).classes('mb-6 bg-green-500 text-white hover:bg-green-600')
            
            # Artists table
            self.table = GenericTable(
                data=self.filtered_artists,
                columns=['name', 'abbreviation', 'created_at'],
                actions=['view', 'edit', 'delete'],
                crud_operations=self.music_service.artist_crud
            )
            
            # Add artist form (hidden by default)
            self.add_form = GenericForm(
                model_class=Artist,
                fields=['name', 'abbreviation', 'persona'],
                submit_action=self._create_artist
            )
            self.add_form.visible = False
    
    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
    
    def _handle_search(self, search_text: str, search_type: str):
        """Handle search functionality"""
        if not search_text.strip():
            self.filtered_artists = self.artists.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_artists = [
                artist for artist in self.artists
                if search_lower in artist.name.lower() or 
                   (artist.abbreviation and search_lower in artist.abbreviation.lower())
            ]
        
        self.table.update_data(self.filtered_artists)
    
    def _load_data(self):
        """Load artists data"""
        try:
            data = self.music_service.list_artists()
            self.table.update_data(data)
        except Exception as e:
            ui.notify(f'Error loading artists: {str(e)}', type='negative')
    
    async def _create_artist(self, **kwargs):
        """Create a new artist"""
        try:
            artist = await self.music_service.create_artist(**kwargs)
            self.artists.append(artist)
            self.filtered_artists.append(artist)
            self.table.add_row(artist)
            self.add_form.visible = False
            ui.notify('Artist created successfully!', type='positive')
        except Exception as e:
            ui.notify(f'Error creating artist: {str(e)}', type='negative')
    
    def _show_add_form(self):
        """Show the add artist form"""
        self.add_form.visible = True
    
    async def refresh_data(self):
        """Refresh artists data"""
        try:
            self.artists = await self.music_service.list_artists()
            self.filtered_artists = self.artists.copy()
            self.table.update_data(self.filtered_artists)
        except Exception as e:
            ui.notify(f'Error loading artists: {str(e)}', type='negative')
