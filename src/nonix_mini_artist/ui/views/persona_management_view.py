"""
Persona Management View - Comprehensive persona creation, editing, and management
"""
from nicegui import ui
from typing import Dict, Any, Optional, List
from ...services.persona_service import AIPersonaService
from ...services.music_service import MusicService
from ...services.tool_registry import ToolRegistry

class PersonaManagementView:
    """Comprehensive persona management interface"""
    
    def __init__(self):
        """Initialize the persona management view"""
        self.persona_service = AIPersonaService()
        self.music_service = MusicService()
        self.tool_registry = ToolRegistry()
        
        # State
        self.personas: List[Dict[str, Any]] = []
        self.artists: List[Dict[str, Any]] = []
        self.available_tools: List[str] = []
        self.editing_persona: Optional[Dict[str, Any]] = None
        self.is_creating = False
        
        # Build the view
        self._build_view()
    
    def _build_view(self):
        """Build the persona management view"""
        with ui.column().classes('w-full p-6') as container:
            self.container = container
            # Header with action buttons
            with ui.row().classes('items-center justify-between mb-6'):
                ui.label('🎭 Persona Management').classes('text-3xl font-bold text-gray-800')
                
                with ui.row().classes('gap-3'):
                    ui.button('🎤 Artist Template', on_click=self._show_artist_template_dialog).classes(
                        'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded-lg'
                    )
                    ui.button('➕ New Persona', on_click=self._show_create_persona_dialog).classes(
                        'px-4 py-2 bg-green-500 text-white hover:bg-green-600 rounded-lg'
                    )
            
            # Personas grid
            self.personas_container = ui.row().classes('flex-wrap gap-4')
            
            # Create/Edit dialog (hidden by default)
            self._build_persona_dialog()
            
            # Artist template dialog (hidden by default)
            self._build_artist_template_dialog()
    
    def _build_persona_dialog(self):
        """Build the persona creation/editing dialog"""
        with ui.dialog() as self.persona_dialog, ui.card().classes('w-full max-w-4xl'):
            # Dialog header
            with ui.row().classes('items-center justify-between mb-4'):
                self.dialog_title = ui.label('Create New Persona').classes('text-xl font-bold')
                ui.button('✕', on_click=self.persona_dialog.close).classes(
                    'w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300'
                )
            
            # Form container
            with ui.column().classes('space-y-4'):
                # Basic Information
                with ui.card().classes('p-4'):
                    ui.label('Basic Information').classes('text-lg font-semibold mb-3')
                    
                    with ui.row().classes('gap-4'):
                        # Name
                        with ui.column().classes('flex-1'):
                            ui.label('Persona Name *').classes('text-sm font-medium mb-1')
                            self.name_input = ui.input(value='', placeholder='Enter persona name').classes('w-full')
                        
                        # Artist Link
                        with ui.column().classes('flex-1'):
                            ui.label('Link to Artist').classes('text-sm font-medium mb-1')
                            self.artist_select = ui.select(
                                options=[],
                                value=None
                            ).classes('w-full')
                
                # Personality Configuration
                with ui.card().classes('p-4'):
                    ui.label('Personality & Behavior').classes('text-lg font-semibold mb-3')
                    
                    # System Prompt
                    ui.label('System Prompt *').classes('text-sm font-medium mb-1')
                    self.system_prompt_input = ui.textarea(
                        value='',
                        placeholder='Describe how this persona should behave and respond...'
                    ).classes('w-full').style('height: 100px')
                    
                    with ui.row().classes('gap-4'):
                        # Personality Traits
                        with ui.column().classes('flex-1'):
                            ui.label('Personality Traits').classes('text-sm font-medium mb-1')
                            self.traits_input = ui.textarea(
                                value='',
                                placeholder='Enter traits separated by commas...'
                            ).classes('w-full').style('height: 80px')
                        
                        # Speaking Style
                        with ui.column().classes('flex-1'):
                            ui.label('Speaking Style').classes('text-sm font-medium mb-1')
                            self.speaking_style_input = ui.textarea(
                                value='',
                                placeholder='Describe the speaking style...'
                            ).classes('w-full').style('height: 80px')
                    
                    # Knowledge Base
                    ui.label('Knowledge Base').classes('text-sm font-medium mb-1')
                    self.knowledge_input = ui.textarea(
                        value='',
                        placeholder='What should this persona know about?'
                    ).classes('w-full').style('height: 80px')
                
                # Tool Permissions
                with ui.card().classes('p-4'):
                    ui.label('Tool Permissions').classes('text-lg font-semibold mb-3')
                    
                    # Tool categories
                    tool_categories = self.tool_registry.get_tool_categories()
                    
                    for category_name, category_info in tool_categories.items():
                        with ui.expansion(category_name, icon='settings').classes('mb-2'):
                            ui.label(category_info['description']).classes('text-sm text-gray-600 mb-2')
                            
                            # Tool checkboxes
                            for tool_name in category_info['tools']:
                                with ui.row().classes('items-center mb-1'):
                                    checkbox = ui.checkbox(tool_name).classes('mr-2')
                                    self._add_tool_checkbox(tool_name, checkbox)
                
                # AI Configuration
                with ui.card().classes('p-4'):
                    ui.label('AI Configuration Overrides').classes('text-lg font-semibold mb-3')
                    
                    with ui.row().classes('gap-4'):
                        # Provider
                        with ui.column().classes('flex-1'):
                            ui.label('AI Provider').classes('text-sm font-medium mb-1')
                            self.ai_provider_select = ui.select(
                                options=['gemini', 'vertex'],
                                value='gemini'
                            ).classes('w-full')
                        
                        # Model
                        with ui.column().classes('flex-1'):
                            ui.label('Model').classes('text-sm font-medium mb-1')
                            self.ai_model_input = ui.input(
                                value='',
                                placeholder='e.g., gemini-1.5-pro'
                            ).classes('w-full')
                    
                    with ui.row().classes('gap-4'):
                        # Temperature
                        with ui.column().classes('flex-1'):
                            ui.label('Temperature (Creativity)').classes('text-sm font-medium mb-1')
                            self.temperature_slider = ui.slider(
                                min=0.0, max=2.0, step=0.1, value=0.7
                            ).classes('w-full')
                            ui.label('0.0 = Focused, 2.0 = Creative').classes('text-xs text-gray-500')
                        
                        # Max Tokens
                        with ui.column().classes('flex-1'):
                            ui.label('Max Response Length').classes('text-sm font-medium mb-1')
                            self.max_tokens_input = ui.number(
                                min=100, max=10000, value=1000, step=100
                            ).classes('w-full')
                
                # Action buttons
                with ui.row().classes('justify-end gap-3 pt-4'):
                    ui.button('Cancel', on_click=self.persona_dialog.close).classes(
                        'px-6 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded-lg'
                    )
                    self.save_button = ui.button('Create Persona', on_click=self._save_persona).classes(
                        'px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600'
                    )
    
    def _add_tool_checkbox(self, tool_name: str, checkbox: ui.checkbox):
        """Add a tool permission checkbox to the form"""
        # Store reference to checkbox for later retrieval
        if not hasattr(self, 'tool_checkboxes'):
            self.tool_checkboxes = {}
        self.tool_checkboxes[tool_name] = checkbox
    
    def _load_data(self):
        """Load personas, artists, and tools data"""
        try:
            # Load personas
            data = self.persona_service.list_personas()
            self._render_personas()
            
            # Load artists
            data = self.music_service.artist_crud.list_all()
            self._update_artist_select()
            
            # Load available tools
            self.available_tools = self.tool_registry.get_available_tools()
            
        except Exception as e:
            ui.notify(f'Failed to load data: {e}', type='error')
    
    def _render_personas(self):
        """Render the personas grid"""
        self.personas_container.clear()
        
        for persona in self.personas:
            with self.personas_container:
                self._create_persona_card(persona)
    
    def _create_persona_card(self, persona: Dict[str, Any]):
        """Create a persona management card"""
        with ui.card().classes('w-80 p-4 bg-white shadow-md hover:shadow-lg transition-shadow'):
            # Header
            with ui.row().classes('items-center justify-between mb-3'):
                ui.label(persona['name']).classes('text-lg font-bold text-gray-800')
                
                # Status indicator
                status_color = "text-green-500" if persona['is_active'] else "text-gray-400"
                ui.label("●").classes(f"text-sm {status_color}")
            
            # Type indicator
            if persona.get('is_artist'):
                if persona.get('artist'):
                    ui.label(f"🎤 Artist: {persona['artist']['name']}").classes('text-sm text-blue-600 mb-2')
                else:
                    ui.label("🎤 Artist Persona").classes('text-sm text-blue-600 mb-2')
            else:
                ui.label("🤖 AI Assistant").classes('text-sm text-green-600 mb-2')
            
            # Quick info
            if persona.get('personality_traits'):
                traits = persona['personality_traits']
                if isinstance(traits, list):
                    traits_text = ', '.join(traits[:3])
                else:
                    traits_text = str(traits)[:50]
                ui.label(f"Traits: {traits_text}").classes('text-sm text-gray-600 mb-2')
            
            # Tool count
            if persona.get('tool_permissions'):
                tools = persona['tool_permissions']
                if isinstance(tools, list):
                    tool_count = len(tools)
                else:
                    tool_count = len(str(tools).split(','))
                ui.label(f"Tools: {tool_count} available").classes('text-sm text-gray-600 mb-3')
            
            # Action buttons
            with ui.row().classes('gap-2'):
                ui.button('✏️ Edit', on_click=lambda p=persona: self._edit_persona(p)).classes(
                    'flex-1 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded'
                )
                ui.button('🗑️ Delete', on_click=lambda p=persona: self._delete_persona(p)).classes(
                    'flex-1 py-2 bg-red-100 text-red-700 hover:bg-red-200 rounded'
                )
                ui.button('🧪 Test', on_click=lambda p=persona: self._test_persona(p)).classes(
                    'flex-1 py-2 bg-green-100 text-green-700 hover:bg-green-200 rounded'
                )
    
    def _update_artist_select(self):
        """Update the artist select dropdown options"""
        if hasattr(self, 'artist_select'):
            options = [{'label': artist['name'], 'value': artist['id']} for artist in self.artists]
            self.artist_select.options = options
    
    def _show_create_persona_dialog(self):
        """Show the persona creation dialog"""
        self.is_creating = True
        self.editing_persona = None
        self.dialog_title.text = 'Create New Persona'
        self.save_button.text = 'Create Persona'
        
        # Clear form
        self._clear_form()
        
        # Show dialog
        self.persona_dialog.open()
    
    def _edit_persona(self, persona: Dict[str, Any]):
        """Edit an existing persona"""
        self.is_creating = False
        self.editing_persona = persona
        self.dialog_title.text = f'Edit Persona: {persona["name"]}'
        self.save_button.text = 'Update Persona'
        
        # Populate form
        self._populate_form(persona)
        
        # Show dialog
        self.persona_dialog.open()
    
    def _clear_form(self):
        """Clear the persona form"""
        if hasattr(self, 'name_input'):
            self.name_input.value = ''
        if hasattr(self, 'artist_select'):
            self.artist_select.value = None
        if hasattr(self, 'system_prompt_input'):
            self.system_prompt_input.value = ''
        if hasattr(self, 'traits_input'):
            self.traits_input.value = ''
        if hasattr(self, 'speaking_style_input'):
            self.speaking_style_input.value = ''
        if hasattr(self, 'knowledge_input'):
            self.knowledge_input.value = ''
        if hasattr(self, 'ai_provider_select'):
            self.ai_provider_select.value = 'gemini'
        if hasattr(self, 'ai_model_input'):
            self.ai_model_input.value = ''
        if hasattr(self, 'temperature_slider'):
            self.temperature_slider.value = 0.7
        if hasattr(self, 'max_tokens_input'):
            self.max_tokens_input.value = 1000
        
        # Clear tool checkboxes
        if hasattr(self, 'tool_checkboxes'):
            for checkbox in self.tool_checkboxes.values():
                checkbox.value = False
    
    def _populate_form(self, persona: Dict[str, Any]):
        """Populate the form with persona data"""
        if hasattr(self, 'name_input'):
            self.name_input.value = persona.get('name', '')
        if hasattr(self, 'artist_select'):
            if persona.get('artist'):
                self.artist_select.value = persona['artist']['id']
            else:
                self.artist_select.value = None
        if hasattr(self, 'system_prompt_input'):
            self.system_prompt_input.value = persona.get('system_prompt', '')
        if hasattr(self, 'traits_input'):
            traits = persona.get('personality_traits', [])
            if isinstance(traits, list):
                self.traits_input.value = ', '.join(traits)
            else:
                self.traits_input.value = str(traits) if traits else ''
        if hasattr(self, 'speaking_style_input'):
            self.speaking_style_input.value = persona.get('speaking_style', '')
        if hasattr(self, 'knowledge_input'):
            self.knowledge_input.value = persona.get('knowledge_base', '')
        
        # AI configuration
        if hasattr(self, 'ai_provider_select'):
            self.ai_provider_select.value = 'gemini'  # Default
        if hasattr(self, 'ai_model_input'):
            self.ai_model_input.value = 'gemini-1.5-pro'  # Default
        if hasattr(self, 'temperature_slider'):
            self.temperature_slider.value = 0.7  # Default
        if hasattr(self, 'max_tokens_input'):
            self.max_tokens_input.value = 1000  # Default
        
        # Tool permissions
        if hasattr(self, 'tool_checkboxes'):
            permissions = persona.get('tool_permissions', [])
            if isinstance(permissions, list):
                for tool_name, checkbox in self.tool_checkboxes.items():
                    checkbox.value = tool_name in permissions
            else:
                # Clear all checkboxes if permissions format is unknown
                for checkbox in self.tool_checkboxes.values():
                    checkbox.value = False
    
    def _save_persona(self):
        """Save the persona (create or update) with enhanced validation"""
        try:
            # Enhanced validation
            validation_errors = []
            
            # Required field validation
            if not self.name_input.value.strip():
                validation_errors.append('Persona name is required')
            
            if not self.system_prompt_input.value.strip():
                validation_errors.append('System prompt is required')
            
            # Length validation
            if len(self.name_input.value.strip()) > 255:
                validation_errors.append('Persona name must be under 255 characters')
            
            if len(self.system_prompt_input.value.strip()) > 5000:
                validation_errors.append('System prompt must be under 5000 characters')
            
            # Tool permissions validation
            selected_tools = self._collect_tool_permissions()
            if not selected_tools:
                validation_errors.append('At least one tool permission must be selected')
            
            # Show validation errors if any
            if validation_errors:
                error_message = 'Please fix the following errors:\n• ' + '\n• '.join(validation_errors)
                ui.notify(error_message, type='error')
                return
            
            # Show saving indicator
            self.save_button.disable()
            self.save_button.text = 'Saving...'
            
            # Collect form data
            persona_data = {
                'name': self.name_input.value.strip(),
                'system_prompt': self.system_prompt_input.value.strip(),
                'personality_traits': self._parse_traits_input(),
                'speaking_style': self.speaking_style_input.value.strip(),
                'knowledge_base': self.knowledge_input.value.strip(),
                'tool_permissions': selected_tools,
                'ai_overrides': self._collect_ai_overrides()
            }
            
            # Handle artist linking
            if self.artist_select.value:
                persona_data['artist_id'] = self.artist_select.value
                persona_data['is_artist'] = True
            else:
                persona_data['is_artist'] = False
            
            if self.is_creating:
                # Create new persona
                self.persona_service.create_persona(**persona_data)
                ui.notify('Persona created successfully!', type='positive')
            else:
                # Update existing persona
                if self.editing_persona:
                    self.persona_service.update_persona(
                        self.editing_persona['id'], **persona_data
                    )
                    ui.notify('Persona updated successfully!', type='positive')
            
            # Close dialog and refresh
            self.persona_dialog.close()
            self._load_data()
            
        except Exception as e:
            ui.notify(f'Failed to save persona: {e}', type='error')
        finally:
            # Re-enable save button
            self.save_button.enable()
            if self.is_creating:
                self.save_button.text = 'Create Persona'
            else:
                self.save_button.text = 'Update Persona'
    
    def _parse_traits_input(self) -> List[str]:
        """Parse traits input into a list"""
        traits_text = self.traits_input.value.strip()
        if not traits_text:
            return []
        
        # Split by commas and clean up
        traits = [trait.strip() for trait in traits_text.split(',') if trait.strip()]
        return traits
    
    def _collect_tool_permissions(self) -> List[str]:
        """Collect selected tool permissions"""
        if not hasattr(self, 'tool_checkboxes'):
            return []
        
        permissions = []
        for tool_name, checkbox in self.tool_checkboxes.items():
            if checkbox.value:
                permissions.append(tool_name)
        
        return permissions
    
    def _collect_ai_overrides(self) -> Dict[str, Any]:
        """Collect AI configuration overrides"""
        overrides = {}
        
        if hasattr(self, 'ai_provider_select') and self.ai_provider_select.value:
            overrides['provider'] = self.ai_provider_select.value
        
        if hasattr(self, 'ai_model_input') and self.ai_model_input.value:
            overrides['model'] = self.ai_model_input.value
        
        if hasattr(self, 'temperature_slider'):
            overrides['temperature'] = self.temperature_slider.value
        
        if hasattr(self, 'max_tokens_input'):
            overrides['max_tokens'] = self.max_tokens_input.value
        
        return overrides
    
    def _delete_persona(self, persona: Dict[str, Any]):
        """Delete a persona with enhanced confirmation and validation"""
        try:
            # Check if persona has active sessions
            from ...services.chat_service import ChatService
            chat_service = ChatService()
            
            active_sessions = chat_service.get_active_sessions(persona['id'])
            
            if active_sessions:
                # Show warning about active sessions
                with ui.dialog() as warning_dialog, ui.card().classes('w-96'):
                    ui.label('⚠️ Active Sessions Found').classes('text-lg font-bold text-orange-600 mb-3')
                    ui.label(f'This persona has {len(active_sessions)} active chat sessions. Deleting the persona will also delete all associated sessions.').classes('text-gray-600 mb-4')
                    
                    with ui.row().classes('justify-end gap-2'):
                        ui.button('Cancel', on_click=warning_dialog.close).classes(
                            'px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded'
                        )
                        ui.button('Delete Anyway', on_click=lambda: self._confirm_delete_persona(persona, warning_dialog)).classes(
                            'px-4 py-2 bg-red-500 text-white hover:bg-red-600 rounded'
                        )
                    
                    warning_dialog.open()
            else:
                # Direct deletion if no active sessions
                self._confirm_delete_persona(persona, None)
                
        except Exception as e:
            ui.notify(f'Failed to check persona sessions: {e}', type='error')
    
    async def _confirm_delete_persona(self, persona: Dict[str, Any], warning_dialog=None):
        """Confirm and execute persona deletion"""
        try:
            # Close warning dialog if open
            if warning_dialog:
                warning_dialog.close()
            
            # Show final confirmation
            with ui.dialog() as confirm_dialog, ui.card().classes('w-96'):
                ui.label('🗑️ Confirm Deletion').classes('text-lg font-bold text-red-600 mb-3')
                ui.label(f'Are you sure you want to delete "{persona["name"]}"? This action cannot be undone.').classes('text-gray-600 mb-4')
                
                with ui.row().classes('justify-end gap-2'):
                    ui.button('Cancel', on_click=confirm_dialog.close).classes(
                        'px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded'
                    )
                    ui.button('Delete', on_click=lambda: self._execute_delete_persona(persona, confirm_dialog)).classes(
                        'px-4 py-2 bg-red-500 text-white hover:bg-red-600 rounded'
                    )
                
                confirm_dialog.open()
                
        except Exception as e:
            ui.notify(f'Failed to show confirmation dialog: {e}', type='error')
    
    def _execute_delete_persona(self, persona: Dict[str, Any], dialog):
        """Execute the actual persona deletion"""
        try:
            # Show deletion progress
            dialog.close()
            
            with ui.dialog() as progress_dialog, ui.card().classes('w-80'):
                ui.label('🗑️ Deleting Persona').classes('text-lg font-bold mb-3')
                with ui.row().classes('items-center'):
                    ui.spinner('dots', size='md').classes('text-blue-500 mr-3')
                    ui.label('Deleting persona and associated data...').classes('text-gray-600')
                progress_dialog.open()
            
            # Delete persona
            success = self.persona_service.delete_persona(persona['id'])
            
            if success:
                progress_dialog.close()
                ui.notify(f'Persona "{persona["name"]}" deleted successfully!', type='positive')
                self._load_data()
            else:
                progress_dialog.close()
                ui.notify('Failed to delete persona', type='error')
                
        except Exception as e:
            ui.notify(f'Failed to delete persona: {e}', type='error')
    
    def _test_persona(self, persona: Dict[str, Any]):
        """Test a persona (placeholder for future implementation)"""
        ui.notify(f'Testing persona: {persona["name"]}. This feature will be implemented in Phase 7.', type='info')
    
    def refresh(self):
        """Refresh the persona management view"""
        self._load_data()

    def _build_artist_template_dialog(self):
        """Build the artist template creation dialog"""
        with ui.dialog() as self.artist_template_dialog, ui.card().classes('w-full max-w-2xl'):
            # Dialog header
            with ui.row().classes('items-center justify-between mb-4'):
                ui.label('🎤 Create Artist Persona Template').classes('text-xl font-bold')
                ui.button('✕', on_click=self.artist_template_dialog.close).classes(
                    'w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300'
                )
            
            # Form container
            with ui.column().classes('space-y-4'):
                # Artist Selection
                with ui.card().classes('p-4'):
                    ui.label('Artist Selection').classes('text-lg font-semibold mb-3')
                    
                    ui.label('Select Artist *').classes('text-sm font-medium mb-1')
                    self.template_artist_select = ui.select(
                        options=[],
                        value=None
                    ).classes('w-full')
                
                # Template Type
                with ui.card().classes('p-4'):
                    ui.label('Template Type').classes('text-lg font-semibold mb-3')
                    
                    ui.label('Choose Template Style *').classes('text-sm font-medium mb-1')
                    self.template_type_select = ui.select(
                        options=[
                            {'label': 'Default Artist', 'value': 'default'},
                            {'label': 'Dancehall Artist', 'value': 'dancehall'},
                            {'label': 'Reggae Artist', 'value': 'reggae'},
                            {'label': 'Hip-Hop Artist', 'value': 'hiphop'}
                        ],
                        value=None,
                        on_change=self._update_template_description
                    ).classes('w-full')
                    
                    # Template descriptions
                    template_descriptions = {
                        'default': 'General artist persona with balanced personality and tools',
                        'dancehall': 'Street-smart dancehall artist with Jamaican patois and culture',
                        'reggae': 'Spiritual reggae artist with wisdom and cultural knowledge',
                        'hiphop': 'Authentic hip-hop artist with street knowledge and culture'
                    }
                    
                    self.template_description_label = ui.label('Select a template type to see description').classes('text-sm text-gray-600 mt-2')
                
                # Customization Options
                with ui.card().classes('p-4'):
                    ui.label('Customization (Optional)').classes('text-lg font-semibold mb-3')
                    
                    ui.label('Custom Name (leave blank for default)').classes('text-sm font-medium mb-1')
                    self.template_custom_name = ui.input(value='', placeholder='e.g., TRC Street Persona').classes('w-full')
                    
                    ui.label('Additional Personality Traits').classes('text-sm font-medium mb-1')
                    self.template_additional_traits = ui.textarea(
                        value='',
                        placeholder='Add extra traits separated by commas...'
                    ).classes('w-full').style('height: 60px')
                
                # Action buttons
                with ui.row().classes('justify-end gap-3 pt-4'):
                    ui.button('Cancel', on_click=self.artist_template_dialog.close).classes(
                        'px-6 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded-lg'
                    )
                    ui.button('Create Template', on_click=self._create_artist_template).classes(
                        'px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600'
                    )

    def _show_artist_template_dialog(self):
        """Show the artist template creation dialog"""
        # Update artist options
        self._update_template_artist_select()
        
        # Clear form
        self.template_custom_name.value = ''
        self.template_additional_traits.value = ''
        self.template_type_select.value = None
        
        # Show dialog
        self.artist_template_dialog.open()
    
    def _update_template_artist_select(self):
        """Update the artist select dropdown for templates"""
        if hasattr(self, 'template_artist_select'):
            options = [{'label': artist['name'], 'value': artist['id']} for artist in self.artists]
            self.template_artist_select.options = options
    
    def _update_template_description(self, event):
        """Update the template description based on selection"""
        if hasattr(self, 'template_description_label'):
            template_descriptions = {
                'default': 'General artist persona with balanced personality and tools',
                'dancehall': 'Street-smart dancehall artist with Jamaican patois and culture',
                'reggae': 'Spiritual reggae artist with wisdom and cultural knowledge',
                'hiphop': 'Authentic hip-hop artist with street knowledge and culture'
            }
            
            selected_value = event.value
            if selected_value and selected_value in template_descriptions:
                self.template_description_label.text = template_descriptions[selected_value]
            else:
                self.template_description_label.text = 'Select a template type to see description'
    
    async def _create_artist_template(self):
        """Create an artist persona using the selected template"""
        try:
            # Validate required fields
            if not self.template_artist_select.value:
                ui.notify('Please select an artist', type='error')
                return
            
            if not self.template_type_select.value:
                ui.notify('Please select a template type', type='error')
                return
            
            # Get template parameters
            artist_id = self.template_artist_select.value
            template_type = self.template_type_select.value
            
            # Prepare customization
            custom_params = {}
            if self.template_custom_name.value.strip():
                custom_params['name'] = self.template_custom_name.value.strip()
            
            if self.template_additional_traits.value.strip():
                additional_traits = [trait.strip() for trait in self.template_additional_traits.value.split(',') if trait.strip()]
                custom_params['personality_traits'] = additional_traits
            
            # Create the artist persona using template
            persona = await self.persona_service.create_artist_persona_template(
                artist_id, template_type, **custom_params
            )
            
            ui.notify(f'Artist persona "{persona.name}" created successfully!', type='positive')
            
            # Close dialog and refresh
            self.artist_template_dialog.close()
            self._load_data()
            
        except Exception as e:
            ui.notify(f'Failed to create artist template: {e}', type='error')

    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
