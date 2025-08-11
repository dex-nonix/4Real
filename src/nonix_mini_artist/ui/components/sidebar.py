"""
Reusable sidebar component
"""
from nicegui import ui
from typing import List, Dict, Callable

class Sidebar:
    """Reusable sidebar navigation component"""
    
    def __init__(self, items: List[Dict] = None):
        """Initialize sidebar with navigation items"""
        self.items = items or []
        self.nav_items = []
        self.navigation_callbacks = {}
        self._build_sidebar()
    
    def set_navigation_callback(self, route: str, callback: Callable):
        """Set a navigation callback for a specific route"""
        self.navigation_callbacks[route] = callback
    
    def _build_sidebar(self):
        """Build the sidebar structure"""
        # Let NiceGUI handle all styling and layout
        with ui.column().classes('w-64 h-full flex-shrink-0') as sidebar_container:
            self.sidebar_container = sidebar_container
            # Logo/Title
            self.title_label = ui.label('🎵 Music Manager').classes('text-xl font-bold mb-8 text-center')
            
            # Navigation items container - this is where nav items will go
            self.nav_container = ui.column().classes('w-full')
            self._create_nav_items()
    
    def _create_nav_items(self):
        """Create navigation items in the existing container"""
        # Clear existing navigation items
        if hasattr(self, 'nav_items'):
            for nav_item in self.nav_items:
                if hasattr(nav_item, 'delete'):
                    nav_item.delete()
        
        self.nav_items = []
        # Create navigation items INSIDE the nav_container
        with self.nav_container:
            for item in self.items:
                nav_item = ui.button(
                    f"{item.get('icon', '📁')} {item.get('title', 'Item')}",
                    on_click=lambda i=item: self._handle_navigation(i)
                ).classes('w-full text-left mb-2')
                self.nav_items.append(nav_item)
    
    def _handle_navigation(self, item: Dict):
        """Handle navigation item click"""
        route = item.get('route', '')
        if route in self.navigation_callbacks:
            self.navigation_callbacks[route]()
        else:
            # Fallback notification
            ui.notify(f"Navigating to {item.get('title', 'Unknown')}", type='info')
    
    def set_items(self, items: List[Dict]):
        """Set navigation items"""
        self.items = items
        # Update navigation items without rebuilding the entire sidebar
        self._create_nav_items()
    
    def add_item(self, item: Dict):
        """Add a navigation item"""
        self.items.append(item)
        self._create_nav_items()
    
    def remove_item(self, title: str):
        """Remove a navigation item by title"""
        self.items = [item for item in self.items if item.get('title') != title]
        self._create_nav_items()
