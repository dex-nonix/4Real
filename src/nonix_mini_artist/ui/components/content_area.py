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
        # Full width, no height constraints, let content expand naturally
        with ui.column().classes('w-full') as container:
            self.container = container
