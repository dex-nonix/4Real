"""
Reusable content area component
"""
from nicegui import ui

class ContentArea:
    """Reusable content area component"""
    
    def __init__(self):
        """Initialize the content area"""
        self._build_content_area()
    
    def _build_content_area(self):
        """Build the content area structure"""
        # Use flex-1 to take remaining space and proper flexbox layout
        with ui.column().classes('flex-1 p-6 bg-gray-100 overflow-auto flex flex-col') as container:
            self.container = container
