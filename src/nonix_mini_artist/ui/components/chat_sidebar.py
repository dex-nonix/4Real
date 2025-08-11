"""
Chat sidebar component for managing AI personas and chat sessions
"""
from nicegui import ui
from typing import List, Dict, Any, Optional, Callable
from ...services.persona_service import AIPersonaService
from ...services.chat_service import ChatService

class ChatSidebar:
    """Chat sidebar with persona tabs and session management"""
    
    def __init__(self):
        """Initialize the chat sidebar"""
        self.persona_service = AIPersonaService()
        self.chat_service = ChatService()
        
        # State
        self.personas: List[Dict[str, Any]] = []
        self.active_persona_id: Optional[int] = None
        self.active_session_id: Optional[int] = None
        self.sessions: Dict[int, List[Dict[str, Any]]] = {}
        
        # Callbacks
        self.on_persona_selected: Optional[Callable] = None
        self.on_session_selected: Optional[Callable] = None
        
        # Build the sidebar
        self._build_sidebar()
        
        # Load initial data
        # Note: This will be called when the component is actually used
        # self._load_personas()  # Commented out to avoid async issues in constructor
    
    def _build_sidebar(self):
        """Build the chat sidebar structure"""
        with ui.column().classes('w-80 bg-gray-50 border-r border-gray-200 p-4'):
            # Header
            with ui.row().classes('items-center justify-between mb-4'):
                ui.label('💬 Chat').classes('text-xl font-bold text-gray-800')
                ui.button('➕', on_click=self._show_add_persona_dialog).classes(
                    'w-8 h-8 rounded-full bg-blue-500 text-white hover:bg-blue-600'
                )
            
            # Personas section
            ui.label('🎭 Personas').classes('text-sm font-semibold text-gray-600 mb-2')
            self.personas_container = ui.column().classes('space-y-2')
            
            # Sessions section (shown when persona is selected)
            ui.separator().classes('my-4')
            self.sessions_section = ui.column().classes('space-y-2')
            self.sessions_section.visible = False
            
            # Add persona button
            ui.button('➕ Add New Persona', on_click=self._show_add_persona_dialog).classes(
                'w-full mt-4 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded-lg py-2'
            )
    
    async def _load_personas(self):
        """Load all available personas"""
        try:
            self.personas = []
            personas = await self.persona_service.list_personas()
            
            for persona in personas:
                persona_data = await self.persona_service.get_persona_with_artist(persona.id)
                if persona_data:
                    self.personas.append(persona_data)
            
            self._render_personas()
        except Exception as e:
            ui.notify(f'Failed to load personas: {e}', type='error')
    
    def _render_personas(self):
        """Render the personas list"""
        self.personas_container.clear()
        
        for persona in self.personas:
            with self.personas_container:
                self._create_persona_tab(persona)
    
    def _create_persona_tab(self, persona: Dict[str, Any]):
        """Create a persona tab"""
        is_active = self.active_persona_id == persona['id']
        
        with ui.card().classes(f'p-3 cursor-pointer transition-all {"bg-blue-100 border-blue-300" if is_active else "bg-white hover:bg-gray-50"}') as persona_card:
            with ui.row().classes('items-center justify-between'):
                # Persona info
                with ui.column().classes('flex-1'):
                    ui.label(persona['name']).classes('font-semibold text-gray-800')
                    
                    # Artist indicator
                    if persona.get('artist'):
                        ui.label(f"🎤 {persona['artist']['name']}").classes('text-xs text-gray-500')
                    else:
                        ui.label("🤖 AI Assistant").classes('text-xs text-gray-500')
                    
                    # Status indicator
                    status_color = "text-green-500" if persona['is_active'] else "text-gray-400"
                    ui.label("●").classes(f"text-xs {status_color}")
                
                # Quick actions
                with ui.row().classes('space-x-1'):
                    ui.button('⚙️', on_click=lambda: self._edit_persona(persona['id'])).classes(
                        'w-6 h-6 text-xs bg-gray-200 hover:bg-gray-300 rounded'
                    )
                    ui.button('🗑️', on_click=lambda: self._delete_persona(persona['id'])).classes(
                        'w-6 h-6 text-xs bg-red-200 hover:bg-red-300 rounded text-red-600'
                    )
            
            # Click handler
            persona_card.on('click', lambda: self._select_persona(persona['id']))
    
    async def _select_persona(self, persona_id: int):
        """Select a persona and load its sessions"""
        self.active_persona_id = persona_id
        self.active_session_id = None
        
        # Update UI
        self._render_personas()
        
        # Load sessions for this persona
        await self._load_persona_sessions(persona_id)
        
        # Show sessions section
        self.sessions_section.visible = True
        
        # Notify parent component
        if self.on_persona_selected:
            self.on_persona_selected(persona_id)
    
    async def _load_persona_sessions(self, persona_id: int):
        """Load chat sessions for a specific persona"""
        try:
            sessions = await self.chat_service.get_active_sessions(persona_id)
            self.sessions[persona_id] = []
            
            for session in sessions:
                session_data = {
                    'id': session.id,
                    'title': session.title,
                    'created_at': session.created_at,
                    'total_messages': session.total_messages,
                    'last_user_message': session.last_user_message,
                    'last_persona_response': session.last_persona_response
                }
                self.sessions[persona_id].append(session_data)
            
            self._render_sessions(persona_id)
        except Exception as e:
            ui.notify(f'Failed to load sessions: {e}', type='error')
    
    def _render_sessions(self, persona_id: int):
        """Render the sessions list for a persona"""
        self.sessions_section.clear()
        
        # Sessions header
        with self.sessions_section:
            ui.label('💬 Chat Sessions').classes('text-sm font-semibold text-gray-600 mb-2')
            
            # Sessions list
            for session in self.sessions.get(persona_id, []):
                self._create_session_tab(session)
            
            # New session button
            ui.button('➕ New Chat', on_click=lambda: self._create_new_session(persona_id)).classes(
                'w-full mt-2 bg-blue-500 text-white hover:bg-blue-600 rounded-lg py-2'
            )
    
    def _create_session_tab(self, session: Dict[str, Any]):
        """Create a session tab"""
        is_active = self.active_session_id == session['id']
        
        with ui.card().classes(f'p-2 cursor-pointer transition-all {"bg-green-100 border-green-300" if is_active else "bg-white hover:bg-gray-50"}') as session_card:
            with ui.column().classes('flex-1'):
                ui.label(session['title']).classes('font-medium text-gray-800 text-sm')
                
                # Session info
                with ui.row().classes('items-center justify-between text-xs text-gray-500'):
                    ui.label(f"{session['total_messages']} messages")
                    
                    # Quick actions
                    with ui.row().classes('space-x-1'):
                        ui.button('📝', on_click=lambda: self._edit_session(session['id'])).classes(
                            'w-5 h-5 text-xs bg-gray-200 hover:bg-gray-300 rounded'
                        )
                        ui.button('🗑️', on_click=lambda: self._delete_session(session['id'])).classes(
                            'w-5 h-5 text-xs bg-red-200 hover:bg-red-300 rounded text-red-600'
                        )
            
            # Click handler
            session_card.on('click', lambda: self._select_session(session['id']))
    
    async def _create_new_session(self, persona_id: int):
        """Create a new chat session for the selected persona"""
        try:
            # Get persona details for session title
            persona = await self.persona_service.get_persona_with_artist(persona_id)
            if not persona:
                ui.notify('Failed to load persona details', type='error')
                return
            
            # Create session title
            if persona.get('artist'):
                title = f"Chat with {persona['artist']['name']} ({persona['name']})"
            else:
                title = f"Chat with {persona['name']}"
            
            # Create new session
            session = await self.chat_service.create_session(persona_id, title)
            
            # Refresh sessions list
            await self._load_persona_sessions(persona_id)
            
            # Select the new session
            if self.on_session_selected:
                self.on_session_selected(session.id)
                
        except Exception as e:
            ui.notify(f'Failed to create session: {e}', type='error')
    
    async def refresh_sessions(self, persona_id: int):
        """Refresh the sessions list for a specific persona"""
        if persona_id == self.active_persona_id:
            await self._load_persona_sessions(persona_id)
    
    def _select_session(self, session_id: int):
        """Select a chat session"""
        self.active_session_id = session_id
        
        # Update UI
        if self.active_persona_id:
            self._render_sessions(self.active_persona_id)
        
        # Notify parent component
        if self.on_session_selected:
            self.on_session_selected(session_id)
    
    def _show_add_persona_dialog(self):
        """Show dialog to add a new persona"""
        # Redirect to persona management view
        ui.notify('Use the Personas menu to create new personas', type='info')
    
    def _edit_persona(self, persona_id: int):
        """Edit a persona"""
        # Redirect to persona management view
        ui.notify('Use the Personas menu to edit personas', type='info')
    
    def _delete_persona(self, persona_id: int):
        """Delete a persona"""
        # Redirect to persona management view
        ui.notify('Use the Personas menu to delete personas', type='info')
    
    def _edit_session(self, session_id: int):
        """Edit a session"""
        # This will be implemented in the chat interface
        ui.notify('Edit session functionality will be implemented in the chat interface', type='info')
    
    def _delete_session(self, session_id: int):
        """Delete a session"""
        # This will be implemented in the chat interface
        ui.notify('Delete session functionality will be implemented in the persona management view', type='info')
    
    def get_active_persona_id(self) -> Optional[int]:
        """Get the currently active persona ID"""
        return self.active_persona_id
    
    def get_active_session_id(self) -> Optional[int]:
        """Get the currently active session ID"""
        return self.active_session_id
    
    def set_callbacks(self, on_persona_selected: Callable = None, on_session_selected: Callable = None):
        """Set callback functions for persona and session selection"""
        self.on_persona_selected = on_persona_selected
        self.on_session_selected = on_session_selected
