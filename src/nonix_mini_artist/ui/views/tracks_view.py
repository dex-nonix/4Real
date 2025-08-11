"""
Tracks view using reusable components
"""
from nicegui import ui
from ..components.generic_table import GenericTable
from ..components.generic_form import GenericForm
from ..components.search_bar import EntitySearchBar
from ...services.music_service import MusicService
from ...ai.service import AIService
from ...ai.models import AIAnalysisRequest
from ...core.models import Track, Album, Artist

class TracksView:
    """Tracks view using reusable components"""
    
    def __init__(self, music_service: MusicService, ai_service: AIService = None):
        """Initialize tracks view"""
        self.music_service = music_service
        self.ai_service = ai_service
        self.tracks = []
        self.filtered_tracks = []
        self.albums = []
        self.artists = []
        self._build_view()
        # Load data after view is built
        self._load_data()
    
    def _build_view(self):
        """Build the tracks view"""
        with ui.column().classes('w-full') as container:
            self.container = container
            # Header
            ui.label('🎵 Tracks').classes('text-3xl font-bold mb-6')
            
            # Search bar
            self.search_bar = EntitySearchBar(
                entity_type="tracks",
                on_search=self._handle_search,
                placeholder="Search tracks by name..."
            )
            
            # Action buttons
            ui.button('➕ Add New Track', on_click=self._show_add_form).classes('mb-6 bg-green-500 text-white hover:bg-green-600')
            ui.button('🤖 AI Analysis', on_click=self._show_ai_analysis).classes('mb-6 bg-purple-500 text-white hover:bg-purple-600')
            
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
                fields=['track_number', 'name', 'album', 'duration'],
                submit_action=self._create_track
            )
            self.add_form.visible = False
            
            # AI analysis form (hidden by default)
            self.ai_form = self._create_ai_analysis_form()
            self.ai_form.visible = False
    
    def _create_ai_analysis_form(self):
        """Create the AI analysis form"""
        with ui.card().classes('w-full max-w-2xl mx-auto p-6') as form:
            ui.label('🤖 AI Analysis').classes('text-2xl font-bold mb-6')
            
            # Track selection
            ui.label('Select Track:').classes('font-bold mb-2')
            track_select = ui.select(
                options=[f"{t.track_number}. {t.name}" for t in self.tracks] if self.tracks else ['No tracks available'],
                value=None,
                label='Track'
            ).classes('w-full mb-4')
            
            # Analysis preset selection
            ui.label('Analysis Type:').classes('font-bold mb-2')
            preset_select = ui.select(
                options=['lyrics_analyzer', 'style_classifier', 'content_generator'],
                value=None,
                label='Analysis Preset'
            ).classes('w-full mb-4')
            
            # Analyze button
            ui.button('🔍 Analyze with AI', on_click=lambda: self._run_track_analysis(
                track_select.value, preset_select.value
            )).classes('w-full bg-purple-500 text-white hover:bg-purple-600')
            
            # Results area
            ui.separator().classes('my-4')
            ui.label('Analysis Results:').classes('font-bold mb-2')
            self.ai_results_area = ui.markdown('').classes('w-full p-4 bg-gray-100 rounded')
            
            return form
    
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
    
    def _load_data(self):
        """Load tracks, albums, and artists data"""
        try:
            # Use synchronous database operations
            self.tracks = list(self.music_service.track_crud.model.select())
            self.filtered_tracks = self.tracks.copy()
            self.albums = list(self.music_service.album_crud.model.select())
            self.artists = list(self.music_service.artist_crud.model.select())
            self.table.update_data(self.filtered_tracks)
            # Update AI form options if it exists
            self._update_ai_form_options()
        except Exception as e:
            ui.notify(f'Error loading data: {str(e)}', type='negative')
    
    def _update_ai_form_options(self):
        """Update AI form options when data changes"""
        if hasattr(self, 'ai_form') and self.ai_form:
            # Find the track select element and update its options
            for child in self.ai_form.children:
                if hasattr(child, 'options') and hasattr(child, 'label') and child.label == 'Track':
                    child.options = [f"{t.track_number}. {t.name}" for t in self.tracks] if self.tracks else ['No tracks available']
                    break
    
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
    
    def _show_ai_analysis(self):
        """Show the AI analysis form"""
        if self.ai_form:
            self.ai_form.visible = True
    
    async def _run_track_analysis(self, track_info: str, preset_name: str):
        """Run AI analysis on a specific track"""
        if not self.ai_service:
            ui.notify('AI service not available', type='warning')
            return
        
        try:
            if not track_info:
                ui.notify('Please select a track', type='warning')
                return
            
            if not preset_name:
                ui.notify('Please select an analysis preset', type='warning')
                return
            
            # Parse track info to get track number
            track_number = int(track_info.split('.')[0])
            track = next((t for t in self.tracks if t.track_number == track_number), None)
            
            if not track:
                ui.notify('Track not found', type='negative')
                return
            
            # Show loading
            self.ai_results_area.content = '🔄 Analyzing track with AI...'
            
            # Prepare content for analysis
            content_parts = []
            if track.raw_lyrics:
                content_parts.append(f"Lyrics: {track.raw_lyrics}")
            if track.name:
                content_parts.append(f"Track Name: {track.name}")
            if track.album:
                content_parts.append(f"Album: {track.album.title}")
                if track.album.artist:
                    content_parts.append(f"Artist: {track.album.artist.name}")
            
            content = "\n\n".join(content_parts)
            
            # Create analysis request
            request = AIAnalysisRequest(
                preset_name=preset_name,
                content=content,
                context={
                    'track_name': track.name,
                    'album': track.album.title if track.album else 'Unknown',
                    'artist': track.album.artist.name if track.album and track.album.artist else 'Unknown'
                }
            )
            
            # Run analysis
            response = await self.ai_service.analyze(request)
            
            if response.success:
                # Display results
                self.ai_results_area.content = f"""
## AI Analysis Results for "{track.name}"

**Analysis Type:** {preset_name.replace('_', ' ').title()}
**Provider:** {response.provider}
**Model:** {response.model}

### Analysis:
{response.content}

**Usage:** {response.usage or 'N/A'}
                """
                ui.notify('AI analysis completed successfully!', type='positive')
            else:
                # Display error
                self.ai_results_area.content = f"""
## Analysis Failed

**Error:** {response.error}
                """
                ui.notify(f'AI analysis failed: {response.error}', type='negative')
                
        except Exception as e:
            self.ai_results_area.content = f"""
## Analysis Error

**Error:** {str(e)}
            """
            ui.notify(f'Error running AI analysis: {str(e)}', type='negative')
    
    async def refresh_data(self):
        """Refresh tracks data"""
        try:
            self.tracks = await self.music_service.list_tracks()
            self.filtered_tracks = self.tracks.copy()
            self.albums = await self.music_service.list_albums()
            self.artists = await self.music_service.list_artists()
            self.table.update_data(self.filtered_tracks)
            # Update AI form options
            self._update_ai_form_options()
        except Exception as e:
            ui.notify(f'Error loading data: {str(e)}', type='negative')

    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
