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
        
        # Load initial data if available
        if hasattr(self, '_load_data'):
            self._load_data()
    
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
        # Create form
        form = GenericForm(
            model_class=self.model_class,
            fields=self.fields,
            submit_action=self._create_entity,
            embedded=True  # Form will be embedded in dialog
        )
        
        # Create dialog with the form
        dialog = GenericDialog(
            title=f"Add New {self.entity_name}",
            content=form,
            confirm_text=f"Create {self.entity_name}",
            on_confirm=lambda: self._handle_form_submit(form),
            width="600px"
        )
        
        dialog.show()
    
    def _handle_form_submit(self, form):
        """Generic form submission handling"""
        form_data = form.get_data()
        if form_data:
            # Call the create method
            asyncio.create_task(self._create_entity(**form_data))
    
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
