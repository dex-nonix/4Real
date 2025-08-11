"""
Persona tab component for individual persona representation
"""
from nicegui import ui
from typing import Dict, Any, Optional, Callable

class PersonaTab:
    """Individual persona tab component"""
    
    def __init__(self, persona_data: Dict[str, Any], on_select: Optional[Callable] = None):
        """Initialize persona tab"""
        self.persona_data = persona_data
        self.on_select = on_select
        self.is_active = False
        
        # Build the tab
        self._build_tab()
    
    def _build_tab(self):
        """Build the persona tab structure"""
        with ui.card().classes('p-3 cursor-pointer transition-all bg-white hover:bg-gray-50') as self.tab_card:
            with ui.row().classes('items-center justify-between'):
                # Persona info
                with ui.column().classes('flex-1'):
                    # Name and type
                    ui.label(self.persona_data['name']).classes('font-semibold text-gray-800')
                    
                    # Artist indicator or AI assistant
                    if self.persona_data.get('artist'):
                        ui.label(f"🎤 {self.persona_data['artist']['name']}").classes('text-xs text-gray-500')
                    else:
                        ui.label("🤖 AI Assistant").classes('text-xs text-gray-500')
                    
                    # Status indicator
                    status_color = "text-green-500" if self.persona_data['is_active'] else "text-gray-400"
                    ui.label("●").classes(f"text-xs {status_color}")
                
                # Quick actions
                with ui.row().classes('space-x-1'):
                    ui.button('⚙️', on_click=self._edit_persona).classes(
                        'w-6 h-6 text-xs bg-gray-200 hover:bg-gray-300 rounded'
                    )
                    ui.button('🗑️', on_click=self._delete_persona).classes(
                        'w-6 h-6 text-xs bg-red-200 hover:bg-red-300 rounded text-red-600'
                    )
            
            # Click handler
            self.tab_card.on('click', self._on_tab_click)
    
    def _on_tab_click(self):
        """Handle tab click"""
        if self.on_select:
            self.on_select(self.persona_data['id'])
    
    def set_active(self, active: bool):
        """Set the tab as active/inactive"""
        self.is_active = active
        
        # Update styling
        if active:
            self.tab_card.classes('bg-blue-100 border-blue-300')
        else:
            self.tab_card.classes('bg-white hover:bg-gray-50')
    
    def _edit_persona(self):
        """Edit persona - redirect to persona management view"""
        # This will be handled by the main app navigation
        ui.notify('Use the Personas menu to edit personas', type='info')
    
    def _delete_persona(self):
        """Delete persona - redirect to persona management view"""
        # This will be handled by the main app navigation
        ui.notify('Use the Personas menu to delete personas', type='info')
    
    def update_data(self, new_data: Dict[str, Any]):
        """Update persona data"""
        self.persona_data = new_data
        # Rebuild the tab with new data
        self.tab_card.clear()
        self._build_tab()
        if self.is_active:
            self.set_active(True)
    
    def get_persona_id(self) -> int:
        """Get the persona ID"""
        return self.persona_data['id']
    
    def get_persona_name(self) -> str:
        """Get the persona name"""
        return self.persona_data['name']
    
    def is_artist_persona(self) -> bool:
        """Check if this is an artist persona"""
        return self.persona_data.get('is_artist', False)
