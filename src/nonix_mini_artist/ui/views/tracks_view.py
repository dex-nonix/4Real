"""
Tracks view using reusable components
"""
from nicegui import ui
from ...components.generic_table import GenericTable
from ...components.generic_form import GenericForm
from ...components.search_bar import EntitySearchBar
from ...services.music_service import MusicService
from ...core.models import Track, Album, Artist

class TracksView:
    """Tracks view using reusable components"""
    
    def __init__(self, music_service: MusicService):
        """Initialize tracks view"""
        self.music_service = music_service
        self.tracks = []
        self.filtered_tracks = []
        self.albums = []
        self.artists = []
        self._build_view()
        self._load_data()
    
    def _build_view(self):
        """Build the tracks view"""
        with ui.column().classes('w-full'):
            # Header
            ui.label('🎵 Tracks').classes('text-3xl font-bold mb-6')
            
            # Search bar
            self.search_bar = EntitySearchBar(
                entity_type="tracks",
                on_search=self._handle_search,
                placeholder="Search tracks by name..."
            )
            
            # Add new track button
            ui.button('➕ Add New Track', on_click=self._show_add_form).classes('mb-6 bg-green-500 text-white hover:bg-green-600')
            
            # Tracks table
            self.table = GenericTable(
                data=self.filtered_tracks,
                columns=['track_number', 'name', 'album', 'duration', 'created_at'],
                actions=['view', 'edit', 'delete'],
                crud_operations=self.music_service.track_crud
            )
            
            # Add track form (hidden by default)
            self.add_form = GenericForm(
                model_class=Track,
                fields=['track_number', 'name', 'album', 'raw_lyrics', 'formatted_lyrics', 'duration'],
                submit_action=self._create_track
            )
            self.add_form.visible = False
    
    def _handle_search(self, search_text: str, search_type: str):
        """Handle search functionality"""
        if not search_text.strip():
            self.filtered_tracks = self.tracks.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_tracks = [
                track for track in self.tracks
                if search_lower in track.name.lower() or 
                   (track.album and search_lower in track.album.title.lower())
            ]
        
        self.table.update_data(self.filtered_tracks)
    
    async def _load_data(self):
        """Load tracks, albums, and artists data"""
        try:
            self.tracks = await self.music_service.list_tracks()
            self.filtered_tracks = self.tracks.copy()
            self.albums = await self.music_service.list_albums()
            self.artists = await self.music_service.list_artists()
            self.table.update_data(self.filtered_tracks)
        except Exception as e:
            ui.notify(f'Error loading data: {str(e)}', type='negative')
    
    async def _create_track(self, **kwargs):
        """Create a new track"""
        try:
            # Handle album selection
            if 'album' in kwargs and isinstance(kwargs['album'], str):
                # Find album by title
                album_title = kwargs['album']
                album = next((a for a in self.albums if a.title == album_title), None)
                if album:
                    kwargs['album_id'] = album.id
                    del kwargs['album']
                else:
                    ui.notify('Album not found. Please select a valid album.', type='negative')
                    return
            
            track = await self.music_service.create_track(**kwargs)
            self.tracks.append(track)
            self.filtered_tracks.append(track)
            self.table.add_row(track)
            self.add_form.visible = False
            ui.notify('Track created successfully!', type='positive')
        except Exception as e:
            ui.notify(f'Error creating track: {str(e)}', type='negative')
    
    def _show_add_form(self):
        """Show the add track form"""
        self.add_form.visible = True
    
    async def refresh_data(self):
        """Refresh tracks data"""
        try:
            self.tracks = await self.music_service.list_tracks()
            self.filtered_tracks = self.tracks.copy()
            self.table.update_data(self.filtered_tracks)
        except Exception as e:
            ui.notify(f'Error loading tracks: {str(e)}', type='negative')
