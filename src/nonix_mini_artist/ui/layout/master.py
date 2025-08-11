"""
Master layout component - reusable across all views
"""
from nicegui import ui
from ..components.sidebar import Sidebar
from ..components.header import Header
from ..components.content_area import ContentArea

class MasterLayout:
    """Reusable master layout with sidebar, header, and content area"""
    
    def __init__(self):
        """Initialize the master layout"""
        self.sidebar = None
        self.header = None
        self.content = None
        self._build_layout()
    
    def _build_layout(self):
        """Build the master layout structure"""
        # Use flexbox layout with proper classes
        with ui.row().classes('w-full h-screen flex'):
            # Sidebar - fixed width, full height
            self.sidebar = Sidebar()
            
            # Main content area - flexible width, full height
            with ui.column().classes('flex-1 h-full flex flex-col'):
                # Header
                self.header = Header()
                
                # Content area - flexible, scrollable
                self.content = ContentArea()
    
    def set_title(self, title: str):
        """Set the page title"""
        if self.header:
            self.header.set_title(title)
    
    def set_user_info(self, user_info: dict):
        """Set user information in header"""
        if self.header:
            self.header.set_user_info(user_info)
    
    def set_sidebar_items(self, items: list):
        """Set sidebar navigation items"""
        if self.sidebar:
            self.sidebar.set_items(items)
    
    def set_content(self, content):
        """Set the main content"""
        if self.content:
            # Clear any existing content first
            self.content.clear()
            # Set new content
            self.content.set_content(content)
    
    def clear_content(self):
        """Clear the main content"""
        if self.content:
            self.content.clear()
