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
        # Remove excessive margins and make it properly responsive
        with ui.column().classes('flex-1 p-2 bg-gray-100 overflow-auto') as container:
            self.container = container
