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
        with ui.row().classes('w-full items-center justify-between') as header_container:
            self.header_container = header_container
            # Title
            self.title_label = ui.label(self.title).classes('text-2xl font-bold')
            
            # User info and actions
            with ui.row().classes('items-center gap-4'):
                if self.user_info:
                    ui.label(f"Welcome, {self.user_info.get('name', 'User')}")
                
                # Settings button
                ui.button('⚙️', on_click=self._show_settings)
                
                # Help buttons container - will be populated later
                self.help_buttons_container = ui.row().classes('items-center gap-2')
    
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

    def add_help_buttons(self, help_system, performance_monitor):
        """Add help and monitoring buttons to the header"""
        # Add buttons to the existing help_buttons_container
        with self.help_buttons_container:
            ui.button('❓ Help', on_click=help_system.show_help_dialog)
            ui.button('⌨️ Shortcuts', on_click=help_system.show_keyboard_shortcuts)
            ui.button('💡 Tips', on_click=help_system.show_quick_tips)
            ui.button('📊 Performance', on_click=performance_monitor.show_performance_dashboard)
            
            # Health indicator
            performance_monitor.show_health_indicator()
