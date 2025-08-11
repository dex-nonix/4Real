"""
Styles view using reusable components
"""
from nicegui import ui
from ..components.generic_table import GenericTable
from ..components.generic_form import GenericForm
from ..components.search_bar import EntitySearchBar
from ...services.music_service import MusicService
from ...core.models import Style

class StylesView:
    """Styles view using reusable components"""
    
    def __init__(self, music_service: MusicService):
        """Initialize styles view"""
        self.music_service = music_service
        self.styles = []
        self.filtered_styles = []
        self._build_view()
    
    def _build_view(self):
        """Build the styles view"""
        with ui.column().classes('w-full') as container:
            self.container = container
            # Header
            ui.label('🏷️ Styles').classes('text-3xl font-bold mb-6')
            
            # Search bar
            self.search_bar = EntitySearchBar(
                entity_type="styles",
                on_search=self._handle_search,
                placeholder="Search styles by name..."
            )
            
            # Add new style button
            ui.button('➕ Add New Style', on_click=self._show_add_form).classes('mb-6 bg-green-500 text-white hover:bg-green-600')
            
            # Styles table
            self.table = GenericTable(
                data=self.filtered_styles,
                columns=['name', 'category', 'description', 'created_at'],
                actions=['view', 'edit', 'delete'],
                crud_operations=self.music_service.style_crud
            )
            
            # Add style form (hidden by default)
            self.add_form = GenericForm(
                model_class=Style,
                fields=['name', 'category', 'description'],
                submit_action=self._create_style
            )
            self.add_form.visible = False
    
    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
    
    def _handle_search(self, search_text: str, search_type: str):
        """Handle search functionality"""
        if not search_text.strip():
            self.filtered_styles = self.styles.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_styles = [
                style for style in self.styles
                if search_lower in style.name.lower() or 
                   (style.category and search_lower in style.category.lower()) or
                   (style.description and search_lower in style.description.lower())
            ]
        
        self.table.update_data(self.filtered_styles)
    
    def _load_data(self):
        """Load styles data"""
        try:
            data = self.music_service.list_styles()
            self.table.update_data(data)
        except Exception as e:
            ui.notify(f'Error loading data: {str(e)}', type='negative')
    
    async def _create_style(self, **kwargs):
        """Create a new style"""
        try:
            style = await self.music_service.create_style(**kwargs)
            self.styles.append(style)
            self.filtered_styles.append(style)
            self.table.add_row(style)
            self.add_form.visible = False
            ui.notify('Style created successfully!', type='positive')
        except Exception as e:
            ui.notify(f'Error creating style: {str(e)}', type='negative')
    
    def _show_add_form(self):
        """Show the add style form"""
        self.add_form.visible = True
    
    async def refresh_data(self):
        """Refresh styles data"""
        try:
            self.styles = await self.music_service.list_styles()
            self.filtered_styles = self.styles.copy()
            self.table.update_data(self.filtered_styles)
        except Exception as e:
            ui.notify(f'Error loading styles: {str(e)}', type='negative')
