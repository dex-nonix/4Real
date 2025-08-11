"""
Generic form component that works with any model
"""
from nicegui import ui
from typing import Dict, Any, Callable, List
from ...core.models import BaseModel

class GenericForm:
    """Reusable form component for any entity"""
    
    def __init__(self, 
                 model_class: type = None,
                 fields: List[str] = None,
                 submit_action: Callable = None,
                 initial_data: Dict = None):
        """Initialize generic form"""
        self.model_class = model_class
        self.fields = fields or []
        self.submit_action = submit_action
        self.initial_data = initial_data or {}
        self.form_data = {}
        self._build_form()
    
    def _build_form(self):
        """Build the form structure"""
        with ui.card():
            ui.label('Add New Item').classes('text-2xl font-bold mb-6')
            
            # Form fields
            for field in self.fields:
                self._add_field(field)
            
            # Submit button
            ui.button('Submit', on_click=self._handle_submit).classes('w-full mt-6')
    
    def _add_field(self, field_name: str):
        """Add a form field"""
        label = field_name.replace('_', ' ').title()
        initial_value = self.initial_data.get(field_name, '')
        
        if field_name in ['description', 'persona', 'raw_lyrics', 'formatted_lyrics']:
            # Text area for long text fields
            ui.textarea(
                label=label,
                value=initial_value or '',
                on_change=lambda e: self._update_field(field_name, e.value)
            ).classes('w-full mb-4')
        elif field_name in ['created_at', 'release_date']:
            # Date picker for date fields
            ui.date(
                label=label,
                value=initial_value or None,
                on_change=lambda e: self._update_field(field_name, e.value)
            ).classes('w-full mb-4')
        elif field_name in ['album_number', 'track_number', 'duration']:
            # Number input for numeric fields
            ui.number(
                label=label,
                value=initial_value or 0,
                on_change=lambda e: self._update_field(field_name, e.value)
            ).classes('w-full mb-4')
        else:
            # Regular text input
            ui.input(
                label=label,
                value=initial_value or '',
                on_change=lambda e: self._update_field(field_name, e.value)
            ).classes('w-full mb-4')
    
    def _update_field(self, field_name: str, value: Any):
        """Update form data when field changes"""
        self.form_data[field_name] = value
    
    def _handle_submit(self):
        """Handle form submission"""
        if self.submit_action:
            try:
                # Call the submit action with form data
                result = self.submit_action(**self.form_data)
                ui.notify('Item created successfully!', type='positive')
                self._reset_form()
            except Exception as e:
                ui.notify(f'Error: {str(e)}', type='negative')
        else:
            ui.notify('Form submitted!', type='info')
    
    def _reset_form(self):
        """Reset the form to initial state"""
        self.form_data = {}
        # In a real app, you'd clear the form fields
    
    def get_data(self) -> Dict[str, Any]:
        """Get current form data"""
        return self.form_data.copy()
    
    def set_data(self, data: Dict[str, Any]):
        """Set form data"""
        self.initial_data = data
        self.form_data = data.copy()
        # In a real app, you'd update the form fields
