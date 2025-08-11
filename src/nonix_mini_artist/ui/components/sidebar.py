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
        self._build_sidebar()
    
    def _build_sidebar(self):
        """Build the sidebar structure"""
        with ui.column().classes('w-64 h-full bg-gray-800 text-white p-4'):
            # Logo/Title
            ui.label('🎵 Music Manager').classes('text-xl font-bold mb-8 text-center')
            
            # Navigation items
            self.nav_items = []
            for item in self.items:
                nav_item = ui.button(
                    f"{item.get('icon', '📁')} {item.get('title', 'Item')}",
                    on_click=lambda i=item: self._handle_navigation(i)
                ).classes('w-full text-left p-3 mb-2 hover:bg-gray-700 rounded')
                self.nav_items.append(nav_item)
    
    def _handle_navigation(self, item: Dict):
        """Handle navigation item click"""
        # This will be handled by the parent component
        # For now, just show a notification
        ui.notify(f"Navigating to {item.get('title', 'Unknown')}", type='info')
    
    def set_items(self, items: List[Dict]):
        """Set navigation items"""
        self.items = items
        # Rebuild sidebar with new items
        if hasattr(self, 'nav_items'):
            for nav_item in self.nav_items:
                nav_item.delete()
        self._build_sidebar()
    
    def add_item(self, item: Dict):
        """Add a navigation item"""
        self.items.append(item)
        self._build_sidebar()
    
    def remove_item(self, title: str):
        """Remove a navigation item by title"""
        self.items = [item for item in self.items if item.get('title') != title]
        self._build_sidebar()
