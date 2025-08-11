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
from .views.ai_settings_view import AISettingsView
from .views.chat_view import ChatView
from .views.persona_management_view import PersonaManagementView
from .components.help_system import HelpSystem
from .components.performance_monitor import PerformanceMonitor
from ..services.music_service import MusicService
from ..ai.service import AIService
from ..core.database import init_database

class MusicManagerApp:
    """Main music manager application"""
    
    def __init__(self):
        """Initialize the application"""
        self.music_service = MusicService()
        self.ai_service = AIService()
        self.layout = None
        self.current_view = None
        
        # Initialize database
        init_database()
        
        # Set up the app
        self._setup_app()
        
        # Initialize AI providers (will be done when needed)
        # Removed asyncio.create_task as it's not compatible with NiceGUI's event loop
    
    def _init_ai_sync(self):
        """Initialize AI providers synchronously"""
        try:
            # Initialize AI providers when first accessed
            self.ai_service.initialize_providers_sync()
        except Exception as e:
            print(f"Failed to initialize AI providers: {e}")
    
    async def _init_ai(self):
        """Initialize AI providers (kept for compatibility)"""
        try:
            await self.ai_service.initialize_providers()
        except Exception as e:
            print(f"Failed to initialize AI providers: {e}")
    
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
            {"title": "Styles", "icon": "🏷️", "route": "/styles"},
            {"title": "AI Settings", "icon": "🤖", "route": "/ai"},
            {"title": "Personas", "icon": "🎭", "route": "/personas"},  # NEW PERSONA MANAGEMENT
            {"title": "Chat", "icon": "💬", "route": "/chat"}
        ]
        self.layout.set_sidebar_items(sidebar_items)
        
        # Help system
        self.help_system = HelpSystem()
        
        # Performance monitor
        self.performance_monitor = PerformanceMonitor()
        
        # Add help and monitoring buttons to header
        with ui.row().classes('items-center gap-2'):
            ui.button('❓ Help', on_click=self.help_system.show_help_dialog).classes(
                'px-3 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg text-sm'
            )
            ui.button('⌨️ Shortcuts', on_click=self.help_system.show_keyboard_shortcuts).classes(
                'px-3 py-2 bg-gray-100 text-gray-700 hover:bg-gray-300 rounded-lg text-sm'
            )
            ui.button('💡 Tips', on_click=self.help_system.show_quick_tips).classes(
                'px-3 py-2 bg-green-100 text-green-700 hover:bg-green-200 rounded-lg text-sm'
            )
            ui.button('📊 Performance', on_click=self.performance_monitor.show_performance_dashboard).classes(
                'px-3 py-2 bg-purple-100 text-purple-700 hover:bg-purple-200 rounded-lg text-sm'
            )
            
            # Health indicator
            self.performance_monitor.show_health_indicator()
        
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
                ui.button('🤖 AI Settings', on_click=lambda: self._show_ai_settings()).classes('px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600')
                ui.button('🎭 Personas', on_click=lambda: self._show_personas()).classes('px-6 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600')
                ui.button('💬 Chat', on_click=lambda: self._show_chat()).classes('px-6 py-3 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600')
            
            # Quick stats
            ui.separator().classes('my-6')
            ui.label('Quick Stats').classes('text-xl font-bold mb-4')
            
            # Load real data for stats - make it synchronous
            self._load_dashboard_stats_sync(dashboard)
    
    def _load_dashboard_stats_sync(self, dashboard):
        """Load real statistics for the dashboard synchronously"""
        try:
            # Initialize AI providers if not already done
            if not hasattr(self, '_ai_initialized'):
                self._init_ai_sync()
                self._ai_initialized = True
            
            # Get AI service status
            ai_providers = self.ai_service.get_providers()
            ai_presets = self.ai_service.get_presets()
            ai_ready = self.ai_service.are_providers_ready()
            
            with ui.row().classes('gap-6'):
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-blue-500')
                    ui.label('Artists').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-green-500')
                    ui.label('Albums').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-purple-500')
                    ui.label('Tracks').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-orange-500')
                    ui.label('Styles').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label(str(len(ai_presets))).classes('text-2xl font-bold text-red-500')
                    ui.label('AI Presets').classes('text-sm text-gray-600')
                    ui.label(f"{'🟢' if ai_ready else '🔴'} AI {'Active' if ai_ready else 'Inactive'}").classes('text-xs text-gray-500')
        except Exception as e:
            # Fallback to zeros if there's an error
            with ui.row().classes('gap-6'):
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-blue-500')
                    ui.label('Artists').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-green-500')
                    ui.label('Albums').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-purple-500')
                    ui.label('Tracks').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-orange-500')
                    ui.label('Styles').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center'):
                    ui.label('0').classes('text-2xl font-bold text-red-500')
                    ui.label('AI Presets').classes('text-sm text-gray-600')
                    ui.label('🔴 AI Inactive').classes('text-xs text-gray-500')
        
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
        tracks_view = TracksView(self.music_service, self.ai_service)
        self.layout.set_content(tracks_view)
        self.current_view = 'tracks'
    
    def _show_styles(self):
        """Show the styles view"""
        self.layout.set_title('Styles')
        styles_view = StylesView(self.music_service)
        self.layout.set_content(styles_view)
        self.current_view = 'styles'
    
    def _show_ai_settings(self):
        """Show the AI settings view"""
        self.layout.set_title('AI Settings')
        ai_settings_view = AISettingsView(self.ai_service)
        self.layout.set_content(ai_settings_view)
        self.current_view = 'ai_settings'
    
    def _show_chat(self):
        """Show the chat view"""
        self.layout.set_title('💬 AI Chat')
        chat_view = ChatView()
        self.layout.set_content(chat_view)
        self.current_view = 'chat'

    def _show_personas(self):
        """Show the persona management view"""
        self.layout.set_content(PersonaManagementView())
        self.current_view = 'personas'

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
