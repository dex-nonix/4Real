"""
Chat interface component for displaying and managing conversations
"""
from nicegui import ui
from typing import List, Dict, Any, Optional, Callable
from ...services.chat_service import ChatService
from ...services.persona_service import AIPersonaService
from ...services.tool_registry import ToolRegistry

class ChatInterface:
    """Chat interface for displaying and managing conversations"""
    
    def __init__(self):
        """Initialize the chat interface"""
        self.chat_service = ChatService()
        self.persona_service = AIPersonaService()
        self.tool_registry = ToolRegistry()
        
        # State
        self.current_session_id: Optional[int] = None
        self.current_persona_id: Optional[int] = None
        self.messages: List[Dict[str, Any]] = []
        self.is_loading = False
        self.typing_indicator = None
        
        # Callbacks
        self.on_message_sent: Optional[Callable] = None
        
        # Build the interface
        self._build_interface()
    
    def _build_interface(self):
        """Build the chat interface structure"""
        with ui.column().classes('flex-1 h-full flex flex-col'):
            # Chat header
            self.chat_header = ui.row().classes('p-4 border-b border-gray-200 bg-white')
            with self.chat_header:
                ui.label('💬 Select a persona to start chatting').classes('text-lg font-semibold text-gray-700')
            
            # Messages area
            self.messages_container = ui.column().classes('flex-1 p-4 space-y-4 overflow-y-auto bg-gray-50')
            
            # Typing indicator (hidden by default)
            self.typing_indicator = ui.row().classes('p-4 text-gray-500 italic')
            with self.typing_indicator:
                ui.label('🤖 AI is typing...').classes('text-sm')
            self.typing_indicator.visible = False
            
            # Input area
            self.input_container = ui.row().classes('p-4 border-t border-gray-200 bg-white')
            with self.input_container:
                # Message input with enhanced features
                self.message_input = ui.textarea(
                    value='',
                    placeholder='Type your message... (Ctrl+Enter to send)'
                ).classes('flex-1 mr-2 resize-none')
                self.message_input.style('height: 60px')  # Set height instead of rows
                
                # Add keyboard shortcuts
                self.message_input.on('keydown', self._handle_keydown)
                
                # Send button
                self.send_button = ui.button(
                    'Send',
                    on_click=self._send_message
                ).classes('px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600')
                
                # Tool button (shown when tools are available)
                self.tool_button = ui.button(
                    '🛠️ Tools',
                    on_click=self._show_tools_panel
                ).classes('px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 mr-2')
                self.tool_button.visible = False
            
            # Tools panel (collapsible)
            self.tools_panel = ui.expansion(
                '🛠️ Available Tools',
                icon='settings'
            ).classes('mx-4 mb-4')
            self.tools_panel.visible = False
            
            with self.tools_panel:
                self.tools_container = ui.column().classes('p-4 space-y-2')
            
            # Artist-specific panel (shown for artist personas)
            self.artist_panel = ui.expansion(
                '🎤 Artist Tools & Starters',
                icon='music_note'
            ).classes('mx-4 mb-4')
            self.artist_panel.visible = False
            
            with self.artist_panel:
                self.artist_container = ui.column().classes('p-4 space-y-2')
    
    def show_typing_indicator(self):
        """Show the typing indicator"""
        if self.typing_indicator:
            self.typing_indicator.visible = True
    
    def hide_typing_indicator(self):
        """Hide the typing indicator"""
        if self.typing_indicator:
            self.typing_indicator.visible = False
    
    async def refresh_messages(self):
        """Refresh the messages display"""
        if self.current_session_id:
            await self._load_messages()
    
    def set_session(self, session_id: int, persona_id: int):
        """Set the current chat session and persona"""
        self.current_session_id = session_id
        self.current_persona_id = persona_id
        
        # Update header
        self._update_header()
        
        # Load messages
        self._load_messages()
        
        # Load available tools
        self._load_available_tools()
        
        # Show tools panel if tools are available
        self.tools_panel.visible = True
    
    def _update_header(self):
        """Update the chat header with current session info"""
        if not self.current_session_id or not self.current_persona_id:
            return
        
        # This will be populated when we load the session details
        self.chat_header.clear()
        with self.chat_header:
            ui.label('💬 Loading...').classes('text-lg font-semibold text-gray-700')
    
    async def _load_messages(self):
        """Load messages for the current session with performance optimization"""
        if not self.current_session_id:
            return
        
        try:
            # Show loading indicator
            self._show_loading_indicator()
            
            # Get messages with limit for performance
            messages = await self.chat_service.get_session_messages(self.current_session_id, limit=100)
            
            # Convert to list of dictionaries for rendering
            self.messages = []
            for message in messages:
                message_data = {
                    'id': message.id,
                    'sender_type': message.sender_type,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'message_type': message.message_type,
                    'tool_used': message.tool_used,
                    'tool_result': message.tool_result,
                    'tool_status': message.tool_status,
                    'metadata': message.metadata
                }
                self.messages.append(message_data)
            
            # Render messages
            self._render_messages()
            
        except Exception as e:
            ui.notify(f'Failed to load messages: {e}', type='error')
            # Show error state
            self._show_error_state(str(e))
        finally:
            # Hide loading indicator
            self._hide_loading_indicator()
    
    def _show_loading_indicator(self):
        """Show loading indicator while loading messages"""
        if not hasattr(self, 'loading_indicator'):
            with self.messages_container:
                with ui.row().classes('justify-center py-8'):
                    with ui.card().classes('bg-blue-50 border border-blue-200 p-4 rounded-lg'):
                        with ui.row().classes('items-center'):
                            ui.spinner('dots', size='lg').classes('text-blue-500 mr-3')
                            ui.label('Loading messages...').classes('text-blue-700 font-medium')
            self.loading_indicator = True
    
    def _hide_loading_indicator(self):
        """Hide loading indicator"""
        if hasattr(self, 'loading_indicator') and self.loading_indicator:
            self.messages_container.clear()
            self.loading_indicator = False
    
    def _show_error_state(self, error_message: str):
        """Show error state when message loading fails"""
        with self.messages_container:
            with ui.row().classes('justify-center py-8'):
                with ui.card().classes('bg-red-50 border border-red-200 p-4 rounded-lg max-w-md'):
                    with ui.column().classes('items-center text-center'):
                        ui.label('❌').classes('text-2xl mb-2')
                        ui.label('Failed to Load Messages').classes('text-red-700 font-medium mb-2')
                        ui.label(error_message).classes('text-red-600 text-sm mb-3')
                        ui.button('🔄 Retry', on_click=self._retry_loading).classes(
                            'px-4 py-2 bg-red-500 text-white hover:bg-red-600 rounded'
                        )
    
    def _retry_loading(self):
        """Retry loading messages"""
        self._load_messages()
    
    def _render_messages(self):
        """Render all messages in the chat"""
        self.messages_container.clear()
        
        if not self.messages:
            with self.messages_container:
                ui.label('No messages yet. Start the conversation!').classes('text-gray-500 text-center py-8')
            return
        
        # Render messages with performance optimization
        for message in self.messages:
            self._render_message(message)
        
        # Auto-scroll to bottom after rendering
        self._scroll_to_bottom()
    
    def _render_message(self, message: Dict[str, Any]):
        """Render a single message with enhanced styling"""
        try:
            sender_type = message.get('sender_type', 'unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            message_type = message.get('message_type', 'text')
            
            # Format timestamp
            if timestamp:
                try:
                    from datetime import datetime
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%H:%M')
                    else:
                        formatted_time = timestamp.strftime('%H:%M')
                except:
                    formatted_time = 'Unknown'
            else:
                formatted_time = 'Unknown'
            
            # Render based on message type
            if message_type == 'tool_result':
                self._render_tool_message(content, formatted_time, message)
            elif sender_type == 'user':
                self._render_user_message(content, formatted_time)
            elif sender_type == 'persona':
                self._render_persona_message(content, formatted_time)
            elif sender_type == 'system':
                self._render_system_message(content, formatted_time)
            else:
                # Fallback for unknown message types
                self._render_unknown_message(content, formatted_time, message)
                
        except Exception as e:
            # Render error message gracefully
            self._render_error_message(f"Failed to render message: {e}")
    
    def _render_user_message(self, content: str, timestamp: str):
        """Render a user message with enhanced styling"""
        with self.messages_container:
            with ui.row().classes('justify-end mb-3'):
                with ui.card().classes('max-w-3xl bg-blue-500 text-white p-3 rounded-lg shadow-md'):
                    # Message content
                    ui.label(content).classes('text-white text-sm break-words')
                    
                    # Timestamp
                    with ui.row().classes('justify-end mt-1'):
                        ui.label(timestamp).classes('text-xs text-blue-100')
    
    def _render_persona_message(self, content: str, timestamp: str):
        """Render a persona message with enhanced styling"""
        with self.messages_container:
            with ui.row().classes('justify-start mb-3'):
                with ui.card().classes('max-w-3xl bg-white border border-gray-200 p-3 rounded-lg shadow-sm'):
                    # Message header
                    with ui.row().classes('items-center mb-2'):
                        ui.label('🤖').classes('mr-2 text-lg')
                        ui.label('AI Persona').classes('text-xs text-gray-500 font-medium')
                    
                    # Message content
                    ui.label(content).classes('text-gray-800 text-sm break-words')
                    
                    # Timestamp
                    with ui.row().classes('justify-start mt-1'):
                        ui.label(timestamp).classes('text-xs text-gray-400')
    
    def _render_tool_message(self, content: str, timestamp: str, message: Dict[str, Any]):
        """Render a tool result message with enhanced styling"""
        tool_name = message.get('tool_used', 'Unknown Tool')
        tool_status = message.get('tool_status', 'unknown')
        
        # Enhanced status colors and icons
        status_config = {
            'success': {'color': 'text-green-600', 'icon': '✅', 'bg': 'bg-green-50', 'border': 'border-green-200'},
            'error': {'color': 'text-red-600', 'icon': '❌', 'bg': 'bg-red-50', 'border': 'border-red-200'},
            'pending': {'color': 'text-yellow-600', 'icon': '⏳', 'bg': 'bg-yellow-50', 'border': 'border-yellow-200'}
        }
        
        config = status_config.get(tool_status, status_config['pending'])
        
        with self.messages_container:
            with ui.row().classes('justify-start mb-3'):
                with ui.card().classes(f'max-w-3xl {config["bg"]} border {config["border"]} p-3 rounded-lg shadow-sm'):
                    # Tool header with enhanced styling
                    with ui.row().classes('items-center justify-between mb-2'):
                        with ui.row().classes('items-center'):
                            ui.label(config['icon']).classes('mr-2')
                            ui.label(f"{tool_name.replace('_', ' ').title()}").classes('font-semibold text-gray-700')
                        
                        ui.label(f"({tool_status})").classes(f"text-xs {config['color']} font-medium")
                    
                    # Tool result content
                    ui.label(content).classes('text-gray-800 text-sm break-words')
                    
                    # Timestamp
                    with ui.row().classes('justify-start mt-1'):
                        ui.label(timestamp).classes('text-xs text-gray-400')
    
    def _render_system_message(self, content: str, timestamp: str):
        """Render a system message with enhanced styling"""
        with self.messages_container:
            with ui.row().classes('justify-center mb-3'):
                with ui.card().classes('bg-gray-100 border border-gray-300 text-gray-600 p-2 rounded-lg max-w-2xl'):
                    with ui.row().classes('items-center'):
                        ui.label('ℹ️').classes('mr-2')
                        ui.label(content).classes('text-sm')
                    
                    ui.label(timestamp).classes('text-xs text-gray-500 mt-1 text-center')
    
    def _render_unknown_message(self, content: str, timestamp: str, message: Dict[str, Any]):
        """Render an unknown message type with fallback styling"""
        with self.messages_container:
            with ui.row().classes('justify-start mb-3'):
                with ui.card().classes('max-w-3xl bg-gray-100 border border-gray-300 p-3 rounded-lg'):
                    ui.label(f"Unknown message type: {message.get('message_type', 'unknown')}").classes('text-xs text-gray-500 mb-1')
                    ui.label(content).classes('text-gray-700 text-sm')
                    ui.label(timestamp).classes('text-xs text-gray-400 mt-1')
    
    def _render_error_message(self, error_content: str):
        """Render an error message"""
        with self.messages_container:
            with ui.row().classes('justify-center mb-3'):
                with ui.card().classes('bg-red-50 border border-red-200 text-red-600 p-2 rounded-lg'):
                    with ui.row().classes('items-center'):
                        ui.label('⚠️').classes('mr-2')
                        ui.label(error_content).classes('text-sm')
    
    async def _update_session_header(self):
        """Update the session header with current information"""
        if not self.current_session_id:
            return
        
        try:
            session = await self.chat_service.get_session(self.current_session_id)
            if not session:
                return
            
            persona = await self.persona_service.get_persona(session.persona_id)
            if not persona:
                return
            
            self.chat_header.clear()
            with self.chat_header:
                with ui.row().classes('items-center justify-between w-full'):
                    # Session info
                    with ui.column():
                        ui.label(f"💬 {session.title}").classes('text-lg font-semibold text-gray-700')
                        ui.label(f"🎭 {persona.name}").classes('text-sm text-gray-500')
                    
                    # Session actions
                    with ui.row().classes('space-x-2'):
                        ui.button('📝 Rename', on_click=lambda: self._rename_session()).classes(
                            'px-3 py-1 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded text-sm'
                        )
                        ui.button('🗑️ Delete', on_click=lambda: self._delete_session()).classes(
                            'px-3 py-1 bg-red-200 text-red-700 hover:bg-red-300 rounded text-sm'
                        )
                        ui.button('📤 Export', on_click=lambda: self._export_session()).classes(
                            'px-3 py-1 bg-green-200 text-green-700 hover:bg-green-300 rounded text-sm'
                        )
        except Exception as e:
            ui.notify(f'Failed to update session header: {e}', type='error')
    
    async def _load_available_tools(self):
        """Load available tools for the current persona"""
        if not self.current_session_id:
            return
        
        try:
            # Get available tools
            available_tools = await self.persona_service.get_available_tools(self.current_persona_id)
            
            # Check if this is an artist persona
            persona = await self.persona_service.get_persona(self.current_persona_id)
            is_artist = persona and persona.is_artist
            
            # Show/hide artist panel
            self.artist_panel.visible = is_artist
            
            if is_artist:
                # Load artist-specific tools and conversation starters
                await self._load_artist_specific_content()
            
            # Render tools panel
            self._render_tools_panel(available_tools)
            
        except Exception as e:
            ui.notify(f'Failed to load tools: {e}', type='error')
    
    async def _load_artist_specific_content(self):
        """Load artist-specific tools and conversation starters"""
        try:
            # Get artist-specific tools
            artist_tools = await self.chat_service.get_artist_specific_tools(self.current_session_id)
            
            # Get conversation starters
            conversation_starters = await self.chat_service.get_artist_conversation_starters(self.current_session_id)
            
            # Render artist panel
            self._render_artist_panel(artist_tools, conversation_starters)
            
        except Exception as e:
            ui.notify(f'Failed to load artist content: {e}', type='error')
    
    def _render_artist_panel(self, artist_tools: Dict[str, Any], conversation_starters: List[str]):
        """Render the artist-specific panel"""
        self.artist_container.clear()
        
        with self.artist_container:
            # Artist Tools Section
            if artist_tools and not artist_tools.get('error'):
                ui.label('🎯 Enhanced Artist Tools').classes('text-lg font-semibold mb-3')
                
                # Tool categories
                for category, tools in artist_tools.get('enhanced_categories', {}).items():
                    if tools:
                        with ui.expansion(category.replace('_', ' ').title(), icon='settings').classes('mb-2'):
                            for tool in tools:
                                with ui.row().classes('items-center mb-1'):
                                    ui.button('▶️', on_click=lambda t=tool: self._execute_tool(t)).classes(
                                        'w-6 h-6 text-xs bg-blue-100 hover:bg-blue-200 rounded mr-2'
                                    )
                                    ui.label(tool.replace('_', ' ').title()).classes('text-sm')
            
            # Conversation Starters Section
            if conversation_starters:
                ui.separator().classes('my-4')
                ui.label('💬 Conversation Starters').classes('text-lg font-semibold mb-3')
                ui.label('Click any starter to begin the conversation:').classes('text-sm text-gray-600 mb-2')
                
                for starter in conversation_starters:
                    ui.button(
                        starter,
                        on_click=lambda s=starter: self._use_conversation_starter(s)
                    ).classes(
                        'w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg mb-2 text-sm'
                    )
    
    def _use_conversation_starter(self, starter: str):
        """Use a conversation starter"""
        # Set the starter text in the input
        self.message_input.value = starter
        
        # Focus the input
        self.message_input.focus()
        
        # Show a notification
        ui.notify('Conversation starter loaded! Click Send when ready.', type='info')
    
    async def _execute_tool(self, tool_name: str):
        """Execute a tool with enhanced error handling and user feedback"""
        if not self.current_session_id:
            ui.notify('Please select a chat session first', type='warning')
            return
        
        try:
            # Show tool execution indicator
            self._show_tool_execution_indicator(tool_name)
            
            # Execute tool with persona context
            result = await self.tool_registry.execute_tool(
                tool_name, 
                persona_id=self.current_persona_id
            )
            
            if result['success']:
                content = str(result['result'])
                status = 'success'
            else:
                content = f"Error: {result['error']}"
                status = 'error'
            
            # Add the result message
            await self.chat_service.add_message(
                session_id=self.current_session_id,
                sender_type='tool_result',
                content=content,
                message_type='tool_result',
                tool_info={
                    'tool_name': tool_name,
                    'result': content,
                    'status': status
                }
            )
            
            # Reload messages to show the new ones
            await self._load_messages()
            
            # Show success notification
            if status == 'success':
                ui.notify(f'Tool {tool_name} executed successfully!', type='positive')
            
        except Exception as e:
            ui.notify(f'Failed to execute tool {tool_name}: {e}', type='error')
            
            # Add error message to chat
            await self.chat_service.add_message(
                session_id=self.current_session_id,
                sender_type='tool_result',
                content=f"Tool execution failed: {str(e)}",
                message_type='tool_result',
                tool_info={
                    'tool_name': tool_name,
                    'result': f"Error: {str(e)}",
                    'status': 'error'
                }
            )
            
            # Reload messages
            await self._load_messages()
        finally:
            # Hide tool execution indicator
            self._hide_tool_execution_indicator()
    
    def _show_tool_execution_indicator(self, tool_name: str):
        """Show tool execution indicator"""
        if not hasattr(self, 'tool_execution_indicator'):
            with self.messages_container:
                with ui.row().classes('justify-center mb-3'):
                    with ui.card().classes('bg-yellow-50 border border-yellow-200 p-3 rounded-lg'):
                        with ui.row().classes('items-center'):
                            ui.spinner('dots', size='md').classes('text-yellow-500 mr-2')
                            ui.label(f'Executing {tool_name.replace("_", " ").title()}...').classes('text-yellow-700 text-sm')
            self.tool_execution_indicator = True
    
    def _hide_tool_execution_indicator(self):
        """Hide tool execution indicator"""
        if hasattr(self, 'tool_execution_indicator') and self.tool_execution_indicator:
            # Remove the indicator by clearing and re-rendering
            self._render_messages()
            self.tool_execution_indicator = False
    
    async def _send_message(self):
        """Send a user message with enhanced validation and feedback"""
        if not self.current_session_id:
            ui.notify('Please select a chat session first', type='warning')
            return
        
        content = self.message_input.value.strip()
        if not content:
            ui.notify('Please enter a message', type='warning')
            return
        
        # Validate message length
        if len(content) > 5000:
            ui.notify('Message too long. Please keep messages under 5000 characters.', type='warning')
            return
        
        try:
            # Disable send button during processing
            self.send_button.disable()
            self.send_button.text = 'Sending...'
            
            # Add user message
            await self.chat_service.add_message(
                session_id=self.current_session_id,
                sender_type='user',
                content=content,
                message_type='text'
            )
            
            # Clear input and focus
            self.message_input.value = ''
            self.message_input.focus()
            
            # Reload messages
            await self._load_messages()
            
            # Notify parent component
            if self.on_message_sent:
                self.on_message_sent(content)
            
            # Show success feedback
            ui.notify('Message sent successfully!', type='positive')
                
        except Exception as e:
            ui.notify(f'Failed to send message: {e}', type='error')
        finally:
            # Re-enable send button
            self.send_button.enable()
            self.send_button.text = 'Send'
    
    def _show_tools_panel(self):
        """Show/hide the tools panel"""
        self.tools_panel.visible = not self.tools_panel.visible
    
    def _render_tools_panel(self, available_tools: List[str]):
        """Render the tools panel with available tools"""
        self.tools_container.clear()
        
        if not available_tools:
            with self.tools_container:
                ui.label('No tools available for this persona').classes('text-gray-500 text-center py-4')
            return
        
        # Group tools by category
        tool_categories = self.tool_registry.get_tool_categories()
        
        for category_name, category_info in tool_categories.items():
            category_tools = [tool for tool in category_info['tools'] if tool in available_tools]
            
            if category_tools:
                with self.tools_container:
                    with ui.expansion(category_name.replace('_', ' ').title(), icon='settings').classes('mb-3'):
                        ui.label(category_info['description']).classes('text-sm text-gray-600 mb-2')
                        
                        with ui.row().classes('flex-wrap gap-2'):
                            for tool in category_tools:
                                ui.button(
                                    tool.replace('_', ' ').title(),
                                    on_click=lambda t=tool: self._execute_tool(t)
                                ).classes('px-3 py-1 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded text-sm')
    
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the messages container"""
        try:
            # Use JavaScript to scroll to bottom
            ui.run_javascript('''
                const container = document.querySelector('.overflow-y-auto');
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            ''')
        except Exception:
            # Fallback: just focus on the last message
            pass
    
    def _rename_session(self):
        """Rename the current session"""
        try:
            # Create a simple input dialog for renaming
            with ui.dialog() as rename_dialog, ui.card().classes('w-96'):
                ui.label('Rename Session').classes('text-lg font-bold mb-3')
                
                new_title = ui.input(
                    value='',
                    placeholder='Enter new session title'
                ).classes('w-full mb-3')
                
                with ui.row().classes('justify-end gap-2'):
                    ui.button('Cancel', on_click=rename_dialog.close).classes(
                        'px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded'
                    )
                    ui.button('Rename', on_click=lambda: self._perform_rename(new_title.value, rename_dialog)).classes(
                        'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded'
                    )
                
                rename_dialog.open()
                
        except Exception as e:
            ui.notify(f'Failed to open rename dialog: {e}', type='error')
    
    async def _perform_rename(self, new_title: str, dialog):
        """Perform the actual session rename"""
        try:
            if not new_title.strip():
                ui.notify('Session title cannot be empty', type='error')
                return
            
            # Update session title
            await self.chat_service.session_crud.update(
                self.current_session_id, 
                title=new_title.strip()
            )
            
            ui.notify('Session renamed successfully!', type='positive')
            dialog.close()
            
            # Refresh the header
            await self._update_session_header()
            
        except Exception as e:
            ui.notify(f'Failed to rename session: {e}', type='error')
    
    def _delete_session(self):
        """Delete the current session"""
        try:
            # Create confirmation dialog
            with ui.dialog() as delete_dialog, ui.card().classes('w-96'):
                ui.label('🗑️ Delete Session').classes('text-lg font-bold mb-3')
                ui.label('Are you sure you want to delete this session? This action cannot be undone.').classes('text-gray-600 mb-4')
                
                with ui.row().classes('justify-end gap-2'):
                    ui.button('Cancel', on_click=delete_dialog.close).classes(
                        'px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded'
                    )
                    ui.button('Delete', on_click=lambda: self._perform_delete(delete_dialog)).classes(
                        'px-4 py-2 bg-red-500 text-white hover:bg-red-600 rounded'
                    )
                
                delete_dialog.open()
                
        except Exception as e:
            ui.notify(f'Failed to open delete dialog: {e}', type='error')
    
    async def _perform_delete(self, dialog):
        """Perform the actual session deletion"""
        try:
            # Delete the session
            success = await self.chat_service.delete_session(self.current_session_id)
            
            if success:
                ui.notify('Session deleted successfully!', type='positive')
                dialog.close()
                
                # Clear the current session
                self.clear_session()
                
                # Notify parent to refresh sidebar
                if hasattr(self, 'on_session_deleted'):
                    self.on_session_deleted()
            else:
                ui.notify('Failed to delete session', type='error')
                
        except Exception as e:
            ui.notify(f'Failed to delete session: {e}', type='error')
    
    def _export_session(self):
        """Export the current session"""
        try:
            # Create export options dialog
            with ui.dialog() as export_dialog, ui.card().classes('w-96'):
                ui.label('📤 Export Session').classes('text-lg font-bold mb-3')
                
                # Export format selection
                ui.label('Export Format:').classes('text-sm font-medium mb-2')
                export_format = ui.select(
                    options=[
                        {'label': 'JSON', 'value': 'json'},
                        {'label': 'Markdown', 'value': 'markdown'}
                    ],
                    value='json'
                ).classes('w-full mb-4')
                
                with ui.row().classes('justify-end gap-2'):
                    ui.button('Cancel', on_click=export_dialog.close).classes(
                        'px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded'
                    )
                    ui.button('Export', on_click=lambda: self._perform_export(export_format.value, export_dialog)).classes(
                        'px-4 py-2 bg-green-500 text-white hover:bg-green-600 rounded'
                    )
                
                export_dialog.open()
                
        except Exception as e:
            ui.notify(f'Failed to open export dialog: {e}', type='error')
    
    async def _perform_export(self, export_format: str, dialog):
        """Perform the actual session export"""
        try:
            # Export the session
            export_data = await self.chat_service.export_session(self.current_session_id, export_format)
            
            if export_data:
                # Create download link
                filename = f"chat_session_{self.current_session_id}.{export_format}"
                
                # For now, just show the data (in a real app, you'd create a download)
                with ui.dialog() as data_dialog, ui.card().classes('w-full max-w-4xl'):
                    ui.label(f'📄 Exported Session ({export_format.upper()})').classes('text-lg font-bold mb-3')
                    
                    if export_format == 'json':
                        ui.code(export_data).classes('w-full h-96 overflow-auto')
                    else:
                        ui.textarea(export_data, readonly=True).classes('w-full h-96')
                    
                    ui.button('Close', on_click=data_dialog.close).classes(
                        'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded mt-3'
                    )
                    
                    data_dialog.open()
                
                ui.notify('Session exported successfully!', type='positive')
                dialog.close()
            else:
                ui.notify('Failed to export session', type='error')
                
        except Exception as e:
            ui.notify(f'Failed to export session: {e}', type='error')
    
    def set_callbacks(self, on_message_sent: Callable = None, on_session_deleted: Callable = None):
        """Set callback functions"""
        self.on_message_sent = on_message_sent
        self.on_session_deleted = on_session_deleted
    
    def clear_session(self):
        """Clear the current session"""
        self.current_session_id = None
        self.current_persona_id = None
        self.messages = []
        
        # Clear UI
        self.chat_header.clear()
        with self.chat_header:
            ui.label('💬 Select a persona to start chatting').classes('text-lg font-semibold text-gray-700')
        
        self.messages_container.clear()
        with self.messages_container:
            ui.label('No messages yet. Start the conversation!').classes('text-gray-500 text-center py-8')
        
        self.tools_panel.visible = False
        self.tool_button.visible = False

    def _handle_keydown(self, e):
        """Handle keyboard shortcuts in the message input"""
        try:
            # Ctrl+Enter to send message
            if e.key == 'Enter' and e.ctrl_key:
                e.preventDefault()
                self._send_message()
            
            # Escape to clear input
            elif e.key == 'Escape':
                e.preventDefault()
                self.message_input.value = ''
                self.message_input.focus()
            
            # Tab to focus tools panel
            elif e.key == 'Tab' and not e.shift_key:
                if self.tools_panel.visible:
                    e.preventDefault()
                    self.tools_panel.focus()
                    
        except Exception:
            # Ignore errors in keyboard handling
            pass
