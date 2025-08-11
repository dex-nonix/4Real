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
        with ui.table().classes('w-full') as self.table:
            # Add columns
            for col in self.columns:
                self.table.add_column(col, col)
            
            # Add action column if actions specified
            if self.actions:
                self.table.add_column('Actions', 'actions')
            
            # Add rows
            self._add_rows()
    
    def _add_rows(self):
        """Add data rows to the table"""
        for item in self.data:
            row_data = {}
            
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
                    row_data[col] = str(value) if value is not None else ''
            
            # Add actions
            if self.actions:
                actions_html = self._create_actions_html(item)
                row_data['actions'] = actions_html
            
            self.table.add_rows([row_data])
    
    def _create_actions_html(self, item: Any) -> str:
        """Create HTML for action buttons"""
        actions = []
        
        if 'view' in self.actions:
            actions.append(f'<button onclick="view_item_{item.id}()" class="px-2 py-1 bg-blue-500 text-white rounded text-sm">👁️</button>')
            # Create view function for this item
            self._create_view_function(item)
        
        if 'edit' in self.actions:
            actions.append(f'<button onclick="edit_item_{item.id}()" class="px-2 py-1 bg-yellow-500 text-white rounded text-sm">✏️</button>')
            # Create edit function for this item
            self._create_edit_function(item)
        
        if 'delete' in self.actions:
            actions.append(f'<button onclick="delete_item_{item.id}()" class="px-2 py-1 bg-red-500 text-white rounded text-sm">🗑️</button>')
            # Create delete function for this item
            self._create_delete_function(item)
        
        return ' '.join(actions)
    
    def _create_view_function(self, item: Any):
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
        self.table.clear()
        self._add_rows()
    
    def add_row(self, item: Any):
        """Add a single row"""
        self.data.append(item)
        row_data = {}
        
        for col in self.columns:
            if hasattr(item, col):
                value = getattr(item, col)
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M')
                elif hasattr(value, 'name'):
                    value = value.name
                row_data[col] = str(value) if value is not None else ''
        
        if self.actions:
            actions_html = self._create_actions_html(item)
            row_data['actions'] = actions_html
        
        self.table.add_rows([row_data])
    
    def clear(self):
        """Clear the table"""
        self.table.clear()
        self.data = []
