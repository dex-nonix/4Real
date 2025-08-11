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
        self.chat_service = None  # Will be initialized when needed
        self.persona_service = None  # Will be initialized when needed
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
    
    def _init_chat_services(self):
        """Initialize chat and persona services when first accessed"""
        try:
            from ..services.chat_service import ChatService
            from ..services.persona_service import AIPersonaService
            
            if self.chat_service is None:
                self.chat_service = ChatService()
            if self.persona_service is None:
                self.persona_service = AIPersonaService()
        except Exception as e:
            print(f"Failed to initialize chat services: {e}")
    
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
        
        # Create the main layout structure ONCE
        self._create_main_layout()
        
        # Set up sidebar navigation
        sidebar_items = [
            {"title": "Dashboard", "icon": "🏠", "route": "/"},
            {"title": "Artists", "icon": "🎤", "route": "/artists"},
            {"title": "Albums", "icon": "💿", "route": "/albums"},
            {"title": "Tracks", "icon": "🎵", "route": "/tracks"},
            {"title": "Styles", "icon": "🏷️", "route": "/styles"},
            {"title": "AI Settings", "icon": "🤖", "route": "/ai"},
            {"title": "Personas", "icon": "🎭", "route": "/personas"},
            {"title": "Chat", "icon": "💬", "route": "/chat"}
        ]
        self.sidebar.set_items(sidebar_items)
        
        # Help system
        self.help_system = HelpSystem()
        
        # Performance monitor
        self.performance_monitor = PerformanceMonitor()
        
        # Add help and monitoring buttons to header
        self.header.add_help_buttons(
            help_system=self.help_system,
            performance_monitor=self.performance_monitor
        )
        
        # Set initial content - show dashboard
        self._show_dashboard()
    
    def _create_main_layout(self):
        """Create the main layout structure - called only once"""
        # Main container
        with ui.row().classes('w-full h-screen flex') as main_container:
            # Sidebar - fixed width, full height
            self.sidebar = Sidebar()
            
            # Main content area - flexible width, full height
            with ui.column().classes('flex-1 h-full flex flex-col'):
                # Header
                self.header = Header()
                
                # Content area - flexible, scrollable
                self.content = ContentArea()
    
    def _show_dashboard(self):
        """Show the dashboard view"""
        # Create dashboard content
        with ui.column().classes('w-full flex flex-col items-center') as dashboard:
            ui.label('🎵 Welcome to Nonix Mini Artist Manager').classes('text-3xl font-bold mb-4 text-center')
            ui.label('Manage your music collection with ease').classes('text-lg text-gray-600 mb-6 text-center')
            
            # Navigation buttons in a proper flexbox row
            with ui.row().classes('gap-4 flex flex-wrap justify-center mb-8'):
                ui.button('🎤 Artists', on_click=lambda: self._show_artists()).classes('px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600')
                ui.button('💿 Albums', on_click=lambda: self._show_albums()).classes('px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600')
                ui.button('🎵 Tracks', on_click=lambda: self._show_tracks()).classes('px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600')
                ui.button('🏷️ Styles', on_click=lambda: self._show_styles()).classes('px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600')
                ui.button('🤖 AI Settings', on_click=lambda: self._show_ai_settings()).classes('px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600')
                ui.button('🎭 Personas', on_click=lambda: self._show_personas()).classes('px-6 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600')
                ui.button('💬 Chat', on_click=lambda: self._show_chat()).classes('px-6 py-3 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600')
            
            # Quick stats
            ui.separator().classes('my-6 w-full')
            ui.label('Quick Stats').classes('text-xl font-bold mb-4 text-center')
            
            # Load real data for stats - make it synchronous
            self._load_dashboard_stats_sync(dashboard)
        
        # Set the content properly
        self.layout.set_content(dashboard)
        self.current_view = 'dashboard'
    
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
            
            # Stats cards in a proper grid layout
            with ui.row().classes('gap-6 w-full flex flex-wrap justify-center'):
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-blue-500')
                    ui.label('Artists').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-green-500')
                    ui.label('Albums').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-purple-500')
                    ui.label('Tracks').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-orange-500')
                    ui.label('Styles').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label(str(len(ai_presets))).classes('text-2xl font-bold text-red-500')
                    ui.label('AI Presets').classes('text-sm text-gray-600')
                    ui.label(f"{'🟢' if ai_ready else '🔴'} AI {'Active' if ai_ready else 'Inactive'}").classes('text-xs text-gray-500')
        except Exception as e:
            # Fallback to zeros if there's an error
            with ui.row().classes('gap-6 w-full flex flex-wrap justify-center'):
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-blue-500')
                    ui.label('Artists').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-green-500')
                    ui.label('Albums').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-purple-500')
                    ui.label('Tracks').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-orange-500')
                    ui.label('Styles').classes('text-sm text-gray-600')
                
                with ui.card().classes('p-4 text-center min-w-[120px]'):
                    ui.label('0').classes('text-2xl font-bold text-red-500')
                    ui.label('AI Presets').classes('text-sm text-gray-600')
                    ui.label('🔴 AI Inactive').classes('text-xs text-gray-500')
        
        # Don't set content here - it's handled in _show_dashboard
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
        self.layout.set_title('Chat')
        # Initialize services if needed
        self._init_chat_services()
        chat_view = ChatView(self.chat_service, self.persona_service)
        self.layout.set_content(chat_view)
        self.current_view = 'chat'
    
    def _show_personas(self):
        """Show the personas view"""
        self.layout.set_title('Personas')
        # Initialize services if needed
        self._init_chat_services()
        persona_view = PersonaManagementView()
        self.layout.set_content(persona_view)
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
