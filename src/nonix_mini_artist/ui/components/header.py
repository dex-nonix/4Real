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

    def add_help_buttons(self, help_system, performance_monitor):
        """Add help and monitoring buttons to the header"""
        # Find the user info and actions row
        if hasattr(self, 'title_label'):
            # Get the parent row and add buttons after the title
            with ui.row().classes('items-center gap-2'):
                ui.button('❓ Help', on_click=help_system.show_help_dialog).classes(
                    'px-3 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg text-sm'
                )
                ui.button('⌨️ Shortcuts', on_click=help_system.show_keyboard_shortcuts).classes(
                    'px-3 py-2 bg-gray-100 text-gray-700 hover:bg-gray-300 rounded-lg text-sm'
                )
                ui.button('💡 Tips', on_click=help_system.show_quick_tips).classes(
                    'px-3 py-2 bg-green-100 text-green-700 hover:bg-green-200 rounded-lg text-sm'
                )
                ui.button('📊 Performance', on_click=performance_monitor.show_performance_dashboard).classes(
                    'px-3 py-2 bg-purple-100 text-purple-700 hover:bg-purple-200 rounded-lg text-sm'
                )
                
                # Health indicator
                performance_monitor.show_health_indicator()
