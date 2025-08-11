"""
Albums view using reusable components
"""
from nicegui import ui
from ..components.generic_table import GenericTable
from ..components.generic_form import GenericForm
from ..components.search_bar import EntitySearchBar
from ...services.music_service import MusicService
from ...core.models import Album, Artist

class AlbumsView:
    """Albums view using reusable components"""
    
    def __init__(self, music_service: MusicService):
        """Initialize albums view"""
        self.music_service = music_service
        self.albums = []
        self.filtered_albums = []
        self.artists = []
        self._build_view()
    
    def _build_view(self):
        """Build the albums view"""
        with ui.column().classes('w-full h-full') as container:
            self.container = container
            # Header
            ui.label('💿 Albums').classes('text-3xl font-bold mb-6')
            
            # Search bar
            self.search_bar = EntitySearchBar(
                entity_type="albums",
                on_search=self._handle_search,
                placeholder="Search albums by title..."
            )
            
            # Add new album button
            ui.button('➕ Add New Album', on_click=self._show_add_form).classes('mb-6')
            
            # Albums table - full width
            self.table = GenericTable(
                data=self.filtered_albums,
                columns=['album_number', 'title', 'artist', 'release_date', 'created_at'],
                actions=['view', 'edit', 'delete'],
                crud_operations=self.music_service.album_crud
            )
            
            # Add album form (hidden by default) - full width
            self.add_form = GenericForm(
                model_class=Album,
                fields=['album_number', 'title', 'artist', 'release_date'],
                submit_action=self._create_album
            )
            self.add_form.visible = False
    
    def _handle_search(self, search_text: str, search_type: str):
        """Handle search functionality"""
        if not search_text.strip():
            self.filtered_albums = self.albums.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_albums = [
                album for album in self.albums
                if search_lower in album.title.lower() or 
                   (album.artist and search_lower in album.artist.name.lower())
            ]
        
        self.table.update_data(self.filtered_albums)
    
    def _load_data(self):
        """Load albums and artists data"""
        try:
            data = self.music_service.list_albums()
            self.table.update_data(data)
        except Exception as e:
            ui.notify(f'Error loading data: {str(e)}', type='negative')
    
    async def _create_album(self, **kwargs):
        """Create a new album"""
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
                    ui.notify('Artist not found. Please select a valid artist.', type='negative')
                    return
            
            album = await self.music_service.create_album(**kwargs)
            self.albums.append(album)
            self.filtered_albums.append(album)
            self.table.add_row(album)
            self.add_form.visible = False
            ui.notify('Album created successfully!', type='positive')
        except Exception as e:
            ui.notify(f'Error creating album: {str(e)}', type='negative')
    
    def _show_add_form(self):
        """Show the add album form"""
        self.add_form.visible = True
    
    async def refresh_data(self):
        """Refresh albums data"""
        try:
            self.albums = await self.music_service.list_albums()
            self.filtered_albums = self.albums.copy()
            self.table.update_data(self.filtered_albums)
        except Exception as e:
            ui.notify(f'Error loading albums: {str(e)}', type='negative')

    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
