"""
Reusable header component
"""
from nicegui import ui
from typing import Dict

class Header:
    """Reusable header component"""
    
    def __init__(self, title: str = "Music Manager", user_info: Dict = None):
        """Initialize header with title and user info"""
        self.title = title
        self.user_info = user_info or {}
        self._build_header()
    
    def _build_header(self):
        """Build the header structure"""
        with ui.row().classes('w-full bg-gray-900 text-white p-4 items-center justify-between'):
            # Title
            self.title_label = ui.label(self.title).classes('text-2xl font-bold')
            
            # User info and actions
            with ui.row().classes('items-center gap-4'):
                if self.user_info:
                    ui.label(f"Welcome, {self.user_info.get('name', 'User')}")
                
                # Settings button
                ui.button('⚙️', on_click=self._show_settings).classes('p-2')
    
    def set_title(self, title: str):
        """Set the header title"""
        self.title = title
        if self.title_label:
            self.title_label.text = title
    
    def set_user_info(self, user_info: Dict):
        """Set user information"""
        self.user_info = user_info
        # In a real app, you'd update the UI to show user info
    
    def _show_settings(self):
        """Show settings dialog"""
        ui.notify("Settings clicked")
