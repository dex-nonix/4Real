"""
Reusable content area component
"""
from nicegui import ui

class ContentArea:
    """Reusable content area component"""
    
    def __init__(self):
        """Initialize the content area"""
        self.current_content = None
        self._build_content_area()
    
    def _build_content_area(self):
        """Build the content area structure"""
        with ui.column().classes('flex-1 p-6 bg-gray-100 overflow-auto'):
            # Default welcome content
            self.current_content = self._create_welcome_content()
    
    def _create_welcome_content(self):
        """Create default welcome content"""
        with ui.column().classes('max-w-4xl mx-auto'):
            ui.label('🎵 Welcome to Nonix Mini Artist Manager').classes('text-3xl font-bold mb-4')
            ui.label('Manage your music collection with ease').classes('text-lg text-gray-600 mb-6')
            
            with ui.row().classes('gap-4'):
                ui.button('🎤 Artists', on_click=lambda: self._show_artists()).classes('px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600')
                ui.button('💿 Albums', on_click=lambda: self._show_albums()).classes('px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600')
                ui.button('🎵 Tracks', on_click=lambda: self._show_tracks()).classes('px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600')
    
    def set_content(self, content):
        """Set the main content"""
        # Clear current content and set new content
        if self.current_content:
            self.current_content.clear()
        
        self.current_content = content
    
    def _show_artists(self):
        """Show artists view"""
        ui.notify("Artists view clicked")
    
    def _show_albums(self):
        """Show albums view"""
        ui.notify("Albums view clicked")
    
    def _show_tracks(self):
        """Show tracks view"""
        ui.notify("Tracks view clicked")
    
    def clear(self):
        """Clear the content area"""
        if self.current_content:
            self.current_content.clear()
        self.current_content = self._create_welcome_content()
