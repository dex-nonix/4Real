"""
Reusable content area component
"""
from nicegui import ui

class ContentArea:
    """Reusable content area component"""
    
    def __init__(self):
        """Initialize the content area"""
        self.current_content = None
        self.content_container = None
        self._build_content_area()
    
    def _build_content_area(self):
        """Build the content area structure"""
        # Use flex-1 to take remaining space and proper flexbox layout
        with ui.column().classes('flex-1 p-6 bg-gray-100 overflow-auto flex flex-col') as container:
            self.content_container = container
            # Don't create default content - let the app handle it
    
    def _create_welcome_content(self):
        """Create default welcome content - removed to avoid duplication"""
        pass
    
    def set_content(self, content):
        """Set the main content"""
        # Clear current content and set new content
        if self.content_container:
            self.content_container.clear()
            # Create new content INSIDE the container
            with self.content_container:
                # If content is a view object with a _build_view method, call it
                if hasattr(content, '_build_view'):
                    content._build_view()
                    self.current_content = content
                elif callable(content):
                    # If content is a callable (function), call it within the container context
                    content()
                    self.current_content = content
                else:
                    # Otherwise, just use the content as is
                    self.current_content = content
    
    def clear(self):
        """Clear the content area"""
        if self.content_container:
            self.content_container.clear()
            # Don't recreate welcome content - let the app handle it
    
    def _show_artists(self):
        """Show artists view"""
        ui.notify("Artists view clicked")
    
    def _show_albums(self):
        """Show albums view"""
        ui.notify("Albums view clicked")
    
    def _show_tracks(self):
        """Show tracks view"""
        ui.notify("Tracks view clicked")
