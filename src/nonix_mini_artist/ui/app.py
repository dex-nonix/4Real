"""
Main NiceGUI application
"""
import asyncio
from nicegui import ui, app
from .layout.master import MasterLayout
from .views.artists_view import ArtistsView
from .views.albums_view import AlbumsView
from .views.tracks_view import TracksView
from .views.styles_view import StylesView
from ..services.music_service import MusicService
from ..core.database import init_database

class MusicManagerApp:
    """Main music manager application"""
    
    def __init__(self):
        """Initialize the application"""
        self.music_service = MusicService()
        self.layout = None
        self.current_view = None
        
        # Initialize database
        init_database()
        
        # Set up the app
        self._setup_app()
    
    def _setup_app(self):
        """Set up the NiceGUI application"""
        # Configure app
        ui.page_title('Nonix Mini Artist Manager')
        
        # Create master layout
        self.layout = MasterLayout()
        
        # Set up sidebar navigation
        sidebar_items = [
            {"title": "Dashboard", "icon": "🏠", "route": "/"},
            {"title": "Artists", "icon": "🎤", "route": "/artists"},
            {"title": "Albums", "icon": "💿", "route": "/albums"},
            {"title": "Tracks", "icon": "🎵", "route": "/tracks"},
            {"title": "Styles", "icon": "🏷️", "route": "/styles"}
        ]
        self.layout.set_sidebar_items(sidebar_items)
        
        # Set initial content
        self._show_dashboard()
    
    def _show_dashboard(self):
        """Show the dashboard view"""
        with ui.column().classes('w-full') as dashboard:
            ui.label('🎵 Welcome to Nonix Mini Artist Manager').classes('text-3xl font-bold mb-4')
            ui.label('Manage your music collection with ease').classes('text-lg text-gray-600 mb-6')
            
            with ui.row().classes('gap-4'):
                ui.button('🎤 Artists', on_click=lambda: self._show_artists()).classes('px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600')
                ui.button('💿 Albums', on_click=lambda: self._show_albums()).classes('px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600')
                ui.button('🎵 Tracks', on_click=lambda: self._show_tracks()).classes('px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600')
                ui.button('🏷️ Styles', on_click=lambda: self._show_styles()).classes('px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600')
            
            # Quick stats
            ui.separator().classes('my-6')
            ui.label('Quick Stats').classes('text-xl font-bold mb-4')
            
            # Load real data for stats
            self._load_dashboard_stats(dashboard)
    
    async def _load_dashboard_stats(self, dashboard):
        """Load real statistics for the dashboard"""
        try:
            # Get counts from the service
            artists_count = await self.music_service.artist_crud.count()
            albums_count = await self.music_service.album_crud.count()
            tracks_count = await self.music_service.track_crud.count()
            styles_count = await self.music_service.style_crud.count()
            
            with ui.row().classes('gap-6'):
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-blue-500">{artists_count}</div>
                    <div class="text-sm text-gray-600">Artists</div>
                ''')
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-green-500">{albums_count}</div>
                    <div class="text-sm text-gray-600">Albums</div>
                ''')
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-purple-500">{tracks_count}</div>
                    <div class="text-sm text-gray-600">Tracks</div>
                ''')
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-orange-500">{styles_count}</div>
                    <div class="text-sm text-gray-600">Styles</div>
                ''')
        except Exception as e:
            # Fallback to zeros if there's an error
            with ui.row().classes('gap-6'):
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-blue-500">0</div>
                    <div class="text-sm text-gray-600">Artists</div>
                ''')
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-green-500">0</div>
                    <div class="text-sm text-gray-600">Albums</div>
                ''')
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-purple-500">0</div>
                    <div class="text-sm text-gray-600">Tracks</div>
                ''')
                ui.card().classes('p-4 text-center').with_html(f'''
                    <div class="text-2xl font-bold text-orange-500">0</div>
                    <div class="text-sm text-gray-600">Styles</div>
                ''')
        
        self.layout.set_content(dashboard)
        self.current_view = 'dashboard'
    
    def _show_artists(self):
        """Show the artists view"""
        self.layout.set_title('Artists')
        artists_view = ArtistsView(self.music_service)
        self.layout.set_content(artists_view)
        self.current_view = 'artists'
    
    def _show_albums(self):
        """Show the albums view"""
        self.layout.set_title('Albums')
        albums_view = AlbumsView(self.music_service)
        self.layout.set_content(albums_view)
        self.current_view = 'albums'
    
    def _show_tracks(self):
        """Show the tracks view"""
        self.layout.set_title('Tracks')
        tracks_view = TracksView(self.music_service)
        self.layout.set_content(tracks_view)
        self.current_view = 'tracks'
    
    def _show_styles(self):
        """Show the styles view"""
        self.layout.set_title('Styles')
        styles_view = StylesView(self.music_service)
        self.layout.set_content(styles_view)
        self.current_view = 'styles'

def main():
    """Main application entry point"""
    # Create and run the app
    app = MusicManagerApp()
    
    # Run the NiceGUI app
    ui.run(
        title='Nonix Mini Artist Manager',
        port=8080,
        show=True,
        reload=False
    )

if __name__ == '__main__':
    main()
