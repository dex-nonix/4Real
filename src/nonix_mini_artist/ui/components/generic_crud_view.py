"""
Generic CRUD view base class to eliminate code duplication
"""
import asyncio
from nicegui import ui
from typing import Dict, Any, List, Optional
from .generic_table import GenericTable
from .generic_form import GenericForm
from .generic_dialog import GenericDialog
from .search_bar import EntitySearchBar
from ...services.music_service import MusicService

class GenericCRUDView:
    """Generic CRUD view base class that eliminates code duplication"""
    
    def __init__(self, music_service: MusicService, entity_config: Dict[str, Any]):
        """Initialize generic CRUD view with entity configuration"""
        self.music_service = music_service
        self.entity_name = entity_config['name']
        self.model_class = entity_config['model']
        self.fields = entity_config['fields']
        self.columns = entity_config['columns']
        self.crud_operations = entity_config['crud']
        self.icon = entity_config.get('icon', '📝')
        self.search_placeholder = entity_config.get('search_placeholder', f'Search {self.entity_name.lower()}s...')
        
        # Data storage
        self.items = []
        self.filtered_items = []
        
        # Build the view
        self._build_view()
        
    
    def _build_view(self):
        """Build the generic CRUD view"""
        with ui.column().classes('w-full') as container:
            self.container = container
            
            # Header
            ui.label(f'{self.icon} {self.entity_name}s').classes('text-3xl font-bold mb-6')
            
            # Search bar
            self.search_bar = EntitySearchBar(
                entity_type=f"{self.entity_name.lower()}s",
                on_search=self._handle_search,
                placeholder=self.search_placeholder
            )
            
            # Add new item button
            ui.button(f'➕ Add New {self.entity_name}', on_click=self._show_add_form).classes('mb-6')
            
            # Items table - full width
            self.table = GenericTable(
                data=self.filtered_items,
                columns=self.columns,
                actions=['view', 'edit', 'delete'],
                crud_operations=self.crud_operations
            )
    
    def _handle_search(self, search_text: str, search_type: str):
        """Generic search functionality"""
        if not search_text.strip():
            self.filtered_items = self.items.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_items = [
                item for item in self.items
                if self._item_matches_search(item, search_lower)
            ]
        
        self.table.update_data(self.filtered_items)
    
    def _item_matches_search(self, item: Any, search_text: str) -> bool:
        """Check if item matches search text - override in subclasses for custom logic"""
        # Default search behavior - check all string fields
        for field in self.fields:
            if hasattr(item, field):
                value = getattr(item, field)
                if value and isinstance(value, str) and search_text in value.lower():
                    return True
                # Handle foreign key relationships
                elif hasattr(value, 'name') and search_text in value.name.lower():
                    return True
        return False
    
    def _show_add_form(self):
        """Generic add form dialog - works for any entity"""
        # Create dialog with form fields built directly
        dialog = GenericDialog(
            title=f"Add New {self.entity_name}",
            content=self._build_form_fields(),
            confirm_text=f"Create {self.entity_name}",
            on_confirm=lambda: self._handle_form_submit(dialog),
            width="600px"
        )
        
        dialog.show()
    
    def _build_form_fields(self):
        """Build form fields for the dialog"""
        form_data = {}
        
        with ui.column().classes('w-full'):
            for field in self.fields:
                label = field.replace('_', ' ').title()
                
                if field in ['description', 'persona', 'raw_lyrics', 'formatted_lyrics']:
                    # Text area for long text fields
                    ui.label(label).classes('text-sm font-medium mb-1')
                    textarea = ui.textarea(
                        value='',
                        on_change=lambda e, f=field: self._update_form_data(f, e.value)
                    ).classes('w-full mb-4')
                elif field in ['created_at', 'release_date']:
                    # Date picker for date fields
                    ui.label(label).classes('text-sm font-medium mb-1')
                    date_input = ui.date(
                        value=None,
                        on_change=lambda e, f=field: self._update_form_data(f, e.value)
                    ).classes('w-full mb-4')
                elif field in ['album_number', 'track_number', 'duration']:
                    # Number input for numeric fields
                    ui.label(label).classes('text-sm font-medium mb-1')
                    number_input = ui.number(
                        value=0,
                        on_change=lambda e, f=field: self._update_form_data(f, e.value)
                    ).classes('w-full mb-4')
                else:
                    # Regular text input
                    ui.label(label).classes('text-sm font-medium mb-1')
                    text_input = ui.input(
                        value='',
                        on_change=lambda e, f=field: self._update_form_data(f, e.value)
                    ).classes('w-full mb-4')
        
        return form_data
    
    def _update_form_data(self, field_name: str, value: Any):
        """Update form data when field changes"""
        if not hasattr(self, '_form_data'):
            self._form_data = {}
        self._form_data[field_name] = value
    
    def _handle_form_submit(self, dialog):
        """Generic form submission handling"""
        if hasattr(self, '_form_data') and self._form_data:
            # Call the create method
            asyncio.create_task(self._create_entity(**self._form_data))
            # Clear form data and close dialog
            self._form_data = {}
            dialog.close()
    
    async def _create_entity(self, **kwargs):
        """Generic entity creation - override in subclasses for custom logic"""
        try:
            # Use the CRUD operations to create the entity
            if hasattr(self.crud_operations, 'create'):
                entity = await self.crud_operations.create(**kwargs)
            else:
                # Fallback to direct model creation
                entity = self.model_class(**kwargs)
                await entity.save()
            
            # Add to local lists
            self.items.append(entity)
            self.filtered_items.append(entity)
            self.table.add_row(entity)
            
            ui.notify(f'{self.entity_name} created successfully!', type='positive')
            
        except Exception as e:
            ui.notify(f'Error creating {self.entity_name.lower()}: {str(e)}', type='negative')
    
    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
    
    def load_initial_data(self):
        """Load initial data - can be called when view is displayed"""
        if hasattr(self, '_load_data'):
            # Schedule async data loading
            asyncio.create_task(self._load_data())
    
    async def refresh_data(self):
        """Generic data refresh - override in subclasses for custom logic"""
        try:
            if hasattr(self.crud_operations, 'list_all'):
                self.items = await self.crud_operations.list_all()
            else:
                # Fallback to direct model query
                self.items = list(self.model_class.select())
            
            self.filtered_items = self.items.copy()
            self.table.update_data(self.filtered_items)
            
        except Exception as e:
            ui.notify(f'Error loading {self.entity_name.lower()}s: {str(e)}', type='negative')
