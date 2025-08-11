"""
Chat view - integrates chat sidebar and interface
"""
from nicegui import ui
from typing import Optional
from ..components.chat_sidebar import ChatSidebar
from ..components.chat_interface import ChatInterface
from ...services.persona_service import AIPersonaService
from ...services.chat_service import ChatService

class ChatView:
    """Main chat view integrating sidebar and interface"""
    
    def __init__(self):
        """Initialize the chat view"""
        self.persona_service = AIPersonaService()
        self.chat_service = ChatService()
        
        # Components
        self.chat_sidebar = None
        self.chat_interface = None
        
        # State
        self.current_persona_id: Optional[int] = None
        self.current_session_id: Optional[int] = None
        
        # Build the view
        self._build_view()
    
    def _build_view(self):
        """Build the chat view"""
        with ui.row().classes('w-full h-full') as container:
            self.container = container
            # Chat sidebar
            self.chat_sidebar = ChatSidebar(
                persona_service=self.persona_service,
                chat_service=self.chat_service,
                on_persona_select=self._on_persona_select,
                on_session_select=self._on_session_select
            )
            
            # Chat interface
            self.chat_interface = ChatInterface()
            
            # Set up callbacks
            self.chat_interface.set_callbacks(
                on_message_sent=self._on_message_sent,
                on_session_deleted=self._on_session_deleted
            )
    
    async def _on_persona_selected(self, persona_id: int):
        """Handle persona selection"""
        self.current_persona_id = persona_id
        self.current_session_id = None
        
        # Clear the chat interface
        self.chat_interface.clear_session()
        
        # Load persona details
        await self._load_persona_details(persona_id)
        
        # Create a new session automatically
        await self._create_new_session(persona_id)
    
    async def _on_session_selected(self, session_id: int):
        """Handle session selection"""
        if not self.current_persona_id:
            return
        
        self.current_session_id = session_id
        
        # Set the session in the chat interface
        self.chat_interface.set_session(session_id, self.current_persona_id)
    
    async def _on_message_sent(self, message: str):
        """Handle message sent and generate AI response"""
        if not self.current_session_id:
            ui.notify('No active session. Please select a persona first.', type='warning')
            return
        
        try:
            # Show typing indicator
            self.chat_interface.show_typing_indicator()
            
            # Generate AI response using the persona
            ai_message = await self.chat_service.generate_ai_response(
                session_id=self.current_session_id,
                user_message=message
            )
            
            if ai_message:
                # Reload messages to show the AI response
                await self.chat_interface.refresh_messages()
                
                # Update session list in sidebar
                await self.chat_sidebar.refresh_sessions(self.current_persona_id)
            else:
                ui.notify('Failed to generate AI response. Please try again.', type='error')
                
        except Exception as e:
            ui.notify(f'Error generating response: {e}', type='error')
        finally:
            # Hide typing indicator
            self.chat_interface.hide_typing_indicator()
    
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
            self.current_session_id = session.id
            
            # Set the session in the chat interface
            self.chat_interface.set_session(session.id, persona_id)
            
            # Refresh sidebar sessions
            await self.chat_sidebar.refresh_sessions(persona_id)
            
            # Add welcome message
            welcome_message = await self._generate_welcome_message(persona)
            if welcome_message:
                await self.chat_service.add_message(
                    session_id=session.id,
                    sender_type='persona',
                    content=welcome_message,
                    message_type='text',
                    metadata={'welcome': True, 'persona_id': persona_id}
                )
                await self.chat_interface.refresh_messages()
            
        except Exception as e:
            ui.notify(f'Failed to create session: {e}', type='error')
    
    async def _generate_welcome_message(self, persona: dict) -> str:
        """Generate a welcome message for the persona"""
        if persona.get('is_artist') and persona.get('artist'):
            return f"Yo! I'm {persona['name']}, representing {persona['artist']['name']}. What's good? How can I help you with the music today?"
        else:
            return f"Hello! I'm {persona['name']}, your AI assistant. How can I help you today?"
    
    async def _load_persona_details(self, persona_id: int):
        """Load and display persona details"""
        try:
            persona = await self.persona_service.get_persona_with_artist(persona_id)
            if persona:
                # Update the interface to show persona info
                # This could show persona details, available tools, etc.
                pass
        except Exception as e:
            ui.notify(f'Failed to load persona details: {e}', type='error')
    
    def get_current_persona_id(self) -> Optional[int]:
        """Get the currently selected persona ID"""
        return self.current_persona_id
    
    def get_current_session_id(self) -> Optional[int]:
        """Get the currently selected session ID"""
        return self.current_session_id
    
    def refresh(self):
        """Refresh the chat view"""
        if self.chat_sidebar:
            # Reload personas and sessions
            pass

    def clear(self):
        """Clear the view content"""
        if hasattr(self, 'container'):
            self.container.clear()
