"""
Generic dialog component for confirmations, details, etc.
"""
from nicegui import ui
from typing import Callable, Optional, Any

class GenericDialog:
    """Reusable dialog component for various purposes"""
    
    def __init__(self, 
                 title: str = "Dialog",
                 content: Any = None,
                 confirm_text: str = "OK",
                 cancel_text: str = "Cancel",
                 on_confirm: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None,
                 width: str = "500px"):
        """Initialize generic dialog"""
        self.title = title
        self.content = content
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.width = width
        self.dialog = None
        self._build_dialog()
    
    def _build_dialog(self):
        """Build the dialog structure"""
        with ui.dialog() as self.dialog:
            with ui.card().classes(f'w-full max-w-2xl p-6 bg-white shadow-2xl rounded-lg'):
                # Header
                ui.label(self.title).classes('text-xl font-bold mb-4 text-center text-gray-800')
                
                # Content
                if self.content:
                    if isinstance(self.content, str):
                        ui.label(self.content).classes('mb-4 text-gray-700')
                    else:
                        ui.add(self.content)
                
                # Actions
                with ui.row().classes('justify-end gap-3 mt-6'):
                    if self.on_cancel:
                        ui.button(self.cancel_text, on_click=self._handle_cancel).classes('px-4 py-2 bg-gray-300 text-gray-700 hover:bg-gray-400 rounded')
                    
                    if self.on_confirm:
                        ui.button(self.confirm_text, on_click=self._handle_confirm).classes('px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded')
                    else:
                        ui.button(self.confirm_text, on_click=self._handle_confirm).classes('px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded')
    
    def _handle_confirm(self):
        """Handle confirm button click"""
        if self.on_confirm:
            self.on_confirm()
        self.dialog.close()
    
    def _handle_cancel(self):
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()
        self.dialog.close()
    
    def show(self):
        """Show the dialog"""
        self.dialog.open()
    
    def close(self):
        """Close the dialog"""
        self.dialog.close()

class ConfirmationDialog(GenericDialog):
    """Specialized dialog for confirmations"""
    
    def __init__(self, 
                 message: str,
                 on_confirm: Callable,
                 title: str = "Confirm Action",
                 confirm_text: str = "Yes",
                 cancel_text: str = "No"):
        """Initialize confirmation dialog"""
        super().__init__(
            title=title,
            content=message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            on_confirm=on_confirm,
            on_cancel=None
        )

class DetailDialog(GenericDialog):
    """Specialized dialog for showing details"""
    
    def __init__(self, 
                 title: str,
                 content: Any,
                 width: str = "600px"):
        """Initialize detail dialog"""
        super().__init__(
            title=title,
            content=content,
            confirm_text="Close",
            cancel_text=None,
            on_confirm=None,
            on_cancel=None,
            width=width
        )
