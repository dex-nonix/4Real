"""
Generic table component that works with any entity
"""
from nicegui import ui
from typing import List, Dict, Any, Callable
from ...crud.helper import CRUDHelper
from .generic_dialog import ConfirmationDialog, DetailDialog

class GenericTable:
    """Reusable table component for any entity"""
    
    def __init__(self, 
                 data: List[Any] = None,
                 columns: List[str] = None,
                 actions: List[str] = None,
                 crud_operations: CRUDHelper = None):
        """Initialize generic table"""
        self.data = data or []
        self.columns = columns or []
        self.actions = actions or []
        self.crud_operations = crud_operations
        self._build_table()
    
    def _build_table(self):
        """Build the table structure"""
        # Create a simple table using NiceGUI components
        with ui.column().classes('w-full') as self.table_container:
            # Table header
            with ui.row().classes('w-full bg-gray-100 p-3 rounded-t-lg font-bold'):
                for col in self.columns:
                    ui.label(col.replace('_', ' ').title()).classes('flex-1 px-2')
                if self.actions:
                    ui.label('Actions').classes('w-32 px-2 text-center')
            
            # Table body container
            self.table_body = ui.column().classes('w-full')
        
        # Add rows
        self._add_rows()
    
    def _add_rows(self):
        """Add data rows to the table"""
        # Clear existing rows
        self.table_body.clear()
        
        for item in self.data:
            with ui.row().classes('w-full p-3 border-b hover:bg-gray-50') as row:
                # Add column data
                for col in self.columns:
                    if hasattr(item, col):
                        value = getattr(item, col)
                        # Format datetime objects
                        if hasattr(value, 'strftime'):
                            value = value.strftime('%Y-%m-%d %H:%M')
                        # Handle foreign key relationships
                        elif hasattr(value, 'name'):
                            value = value.name
                        ui.label(str(value) if value is not None else '').classes('flex-1 px-2')
                    else:
                        ui.label('').classes('flex-1 px-2')
                
                # Add action buttons
                if self.actions:
                    with ui.row().classes('w-32 justify-center gap-1'):
                        if 'view' in self.actions:
                            ui.button('👁️', on_click=lambda i=item: self._view_item(i)).classes('px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600')
                        if 'edit' in self.actions:
                            ui.button('✏️', on_click=lambda i=item: self._edit_item(i)).classes('px-2 py-1 bg-yellow-500 text-white text-xs rounded hover:bg-yellow-600')
                        if 'delete' in self.actions:
                            ui.button('🗑️', on_click=lambda i=item: self._delete_item(i)).classes('px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600')
    
    def _view_item(self, item: Any):
        """View item details"""
        content = self._create_detail_content(item)
        dialog = DetailDialog(
            title=f"View {item.__class__.__name__}",
            content=content
        )
        dialog.show()
    
    def _edit_item(self, item: Any):
        """Edit item (placeholder for future implementation)"""
        ui.notify(f'Edit {item.__class__.__name__} functionality coming soon!', type='info')
    
    def _delete_item(self, item: Any):
        """Delete item with confirmation"""
        dialog = ConfirmationDialog(
            message=f"Are you sure you want to delete this {item.__class__.__name__.lower()}?",
            on_confirm=lambda: self._perform_delete(item),
            title="Confirm Delete"
        )
        dialog.show()
    
    # Removed old HTML-based method
        """Create a view function for the item"""
        def view_item():
            # Create detail dialog
            content = self._create_detail_content(item)
            dialog = DetailDialog(
                title=f"View {item.__class__.__name__}",
                content=content
            )
            dialog.show()
        
        # Store the function reference
        setattr(self, f'view_item_{item.id}', view_item)
    
    def _create_edit_function(self, item: Any):
        """Create an edit function for the item"""
        def edit_item():
            # For now, just show a notification
            ui.notify(f'Edit {item.__class__.__name__} functionality coming soon!', type='info')
        
        # Store the function reference
        setattr(self, f'edit_item_{item.id}', edit_item)
    
    def _create_delete_function(self, item: Any):
        """Create a delete function for the item"""
        def delete_item():
            # Create confirmation dialog
            dialog = ConfirmationDialog(
                message=f"Are you sure you want to delete this {item.__class__.__name__.lower()}?",
                on_confirm=lambda: self._perform_delete(item),
                title="Confirm Delete"
            )
            dialog.show()
        
        # Store the function reference
        setattr(self, f'delete_item_{item.id}', delete_item)
    
    def _create_detail_content(self, item: Any) -> Any:
        """Create content for detail dialog"""
        with ui.column().classes('w-full') as content:
            for col in self.columns:
                if hasattr(item, col):
                    value = getattr(item, col)
                    # Format datetime objects
                    if hasattr(value, 'strftime'):
                        value = value.strftime('%Y-%m-%d %H:%M')
                    # Handle foreign key relationships
                    elif hasattr(value, 'name'):
                        value = value.name
                    
                    with ui.row().classes('w-full py-2 border-b'):
                        ui.label(f"{col.replace('_', ' ').title()}:").classes('font-bold w-32')
                        ui.label(str(value) if value is not None else '').classes('flex-1')
        
        return content
    
    async def _perform_delete(self, item: Any):
        """Perform the actual delete operation"""
        if self.crud_operations:
            try:
                success = await self.crud_operations.delete(item.id)
                if success:
                    ui.notify(f'{item.__class__.__name__} deleted successfully!', type='positive')
                    # Remove from data and refresh table
                    self.data.remove(item)
                    self.update_data(self.data)
                else:
                    ui.notify(f'Failed to delete {item.__class__.__name__}', type='negative')
            except Exception as e:
                ui.notify(f'Error deleting {item.__class__.__name__}: {str(e)}', type='negative')
        else:
            ui.notify('Delete operation not available', type='warning')
    
    def update_data(self, new_data: List[Any]):
        """Update table data"""
        self.data = new_data
        self._add_rows()
    
    def add_row(self, item: Any):
        """Add a single row"""
        self.data.append(item)
        # Rebuild the entire table to ensure proper layout
        self._add_rows()
    
    def clear(self):
        """Clear the table"""
        self.data = []
        self.table_body.clear()
