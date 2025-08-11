"""
Main NiceGUI application
"""
import asyncio
from nicegui import ui, app
from .components.sidebar import Sidebar
from .components.header import Header
from .components.content_area import ContentArea
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
        self.sidebar = None
        self.header = None
        self.content = None
        
        # Initialize database
        init_database()
        
        # Set up the app
        self._setup_app()
    
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
        """Set up the NiceGUI application with proper page routing"""
        # Configure app
        ui.page_title('Nonix Mini Artist Manager')
        
        # Add global CSS to disable scrollbars
        ui.add_head_html('''
            <style>
                /* Disable scrollbars globally */
                ::-webkit-scrollbar {
                    display: none;
                }
                * {
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                }
                /* Ensure no height constraints cause scrollbars */
                body, html {
                    overflow-x: hidden;
                    overflow-y: auto;
                }
                /* Responsive layout */
                .responsive-container {
                    max-width: 100%;
                    padding: 0 1rem;
                }
                @media (max-width: 768px) {
                    .responsive-container {
                        padding: 0 0.5rem;
                    }
                }
            </style>
        ''')
        
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
        
        # Set up navigation callbacks
        self.sidebar.set_navigation_callback("/", self._show_dashboard)
        self.sidebar.set_navigation_callback("/artists", self._show_artists)
        self.sidebar.set_navigation_callback("/albums", self._show_albums)
        self.sidebar.set_navigation_callback("/tracks", self._show_tracks)
        self.sidebar.set_navigation_callback("/styles", self._show_styles)
        self.sidebar.set_navigation_callback("/ai", self._show_ai_settings)
        self.sidebar.set_navigation_callback("/personas", self._show_personas)
        self.sidebar.set_navigation_callback("/chat", self._show_chat)
        
        # Set initial view
        self._show_dashboard()
    
    def _create_main_layout(self):
        """Create the main layout structure"""
        # Create main container with proper responsive layout - NO height constraints
        with ui.row().classes('w-full') as main_container:
            # Sidebar - fixed width, no height constraint
            self.sidebar = Sidebar()
            
            # Main content area - take full remaining width, no height constraint
            with ui.column().classes('flex-1') as content_container:
                # Header
                self.header = Header()
                
                # Content area - full width, no height constraint
                self.content = ContentArea()
        
        # Store references
        self.main_container = main_container
        self.content_container = content_container
    
    def _show_dashboard(self):
        """Show the dashboard view"""
        self.header.set_title('Dashboard')
        # Clear content and show dashboard
        self.content.container.clear()
        with self.content.container:
            DashboardView(self.music_service, self.ai_service, self)
    
    def _show_artists(self):
        """Show the artists view"""
        self.header.set_title('Artists')
        # Clear content and show artists
        self.content.container.clear()
        with self.content.container:
            ArtistsView(self.music_service)
    
    def _show_albums(self):
        """Show the albums view"""
        self.header.set_title('Albums')
        # Clear content and show albums
        self.content.container.clear()
        with self.content.container:
            AlbumsView(self.music_service)
    
    def _show_tracks(self):
        """Show the tracks view"""
        self.header.set_title('Tracks')
        # Clear content and show tracks
        self.content.container.clear()
        with self.content.container:
            TracksView(self.music_service, self.ai_service)
    
    def _show_styles(self):
        """Show the styles view"""
        self.header.set_title('Styles')
        # Clear content and show styles
        self.content.container.clear()
        with self.content.container:
            StylesView(self.music_service)
    
    def _show_ai_settings(self):
        """Show the AI settings view"""
        self.header.set_title('AI Settings')
        # Clear content and show AI settings
        self.content.container.clear()
        with self.content.container:
            AISettingsView(self.ai_service)
    
    def _show_chat(self):
        """Show the chat view"""
        self.header.set_title('Chat')
        # Initialize services if needed
        self._init_chat_services()
        # Clear content and show chat
        self.content.container.clear()
        with self.content.container:
            ChatView(self.chat_service, self.persona_service)
    
    def _show_personas(self):
        """Show the personas view"""
        self.header.set_title('Personas')
        # Initialize services if needed
        self._init_chat_services()
        # Clear content and show personas
        self.content.container.clear()
        with self.content.container:
            PersonaManagementView()

class DashboardView:
    """Dashboard view component"""
    
    def __init__(self, music_service, ai_service, app):
        """Initialize dashboard view"""
        self.music_service = music_service
        self.ai_service = ai_service
        self.app = app  # Reference to parent app for navigation
        self._build_view()
    
    def _build_view(self):
        """Build the dashboard view"""
        with ui.column().classes('w-full') as container:
            self.container = container
            
            ui.label('🎵 Welcome to Nonix Mini Artist Manager').classes('text-3xl font-bold mb-4 text-center')
            ui.label('Manage your music collection with ease').classes('text-lg text-gray-600 mb-6 text-center')
            
            # Navigation buttons in a proper flexbox row
            with ui.row().classes('gap-4 flex flex-wrap justify-center mb-8'):
                ui.button('🎤 Artists', on_click=lambda: self.app._show_artists())
                ui.button('💿 Albums', on_click=lambda: self.app._show_albums())
                ui.button('🎵 Tracks', on_click=lambda: self.app._show_tracks())
                ui.button('🏷️ Styles', on_click=lambda: self.app._show_styles())
                ui.button('🤖 AI Settings', on_click=lambda: self.app._show_ai_settings())
                ui.button('🎭 Personas', on_click=lambda: self.app._show_personas())
                ui.button('💬 Chat', on_click=lambda: self.app._show_chat())
            
            # Quick stats
            ui.separator().classes('my-6 w-full')
            ui.label('Quick Stats').classes('text-xl font-bold mb-4 text-center')
            
            # Load real data for stats
            self._load_dashboard_stats()
    
    def _load_dashboard_stats(self):
        """Load dashboard statistics"""
        try:
            # Initialize AI providers if not already done
            if not hasattr(self.ai_service, '_ai_initialized'):
                self.ai_service.initialize_providers_sync()
                self.ai_service._ai_initialized = True
            
            # Get AI service status
            ai_providers = self.ai_service.get_providers()
            ai_presets = self.ai_service.get_presets()
            ai_ready = self.ai_service.are_providers_ready()
            
            # Stats cards in a proper grid layout
            with ui.row().classes('gap-6 w-full flex flex-wrap justify-center'):
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Artists')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Albums')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Tracks')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Styles')
                
                with ui.card():
                    ui.label(str(len(ai_presets))).classes('text-2xl font-bold')
                    ui.label('AI Presets')
                    ui.label(f"{'🟢' if ai_ready else '🔴'} AI {'Active' if ai_ready else 'Inactive'}")
        except Exception as e:
            # Fallback to zeros if there's an error
            with ui.row().classes('gap-6 w-full flex flex-wrap justify-center'):
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Artists')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Albums')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Tracks')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('Styles')
                
                with ui.card():
                    ui.label('0').classes('text-2xl font-bold')
                    ui.label('AI Presets')
                    ui.label('🔴 AI Inactive')
    
    # Note: Navigation methods are handled by the parent MusicManagerApp class

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
