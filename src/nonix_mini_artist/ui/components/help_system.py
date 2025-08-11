"""
Help System Component - Comprehensive documentation and user guidance
"""
from nicegui import ui
from typing import Dict, Any, List

class HelpSystem:
    """Comprehensive help and documentation system"""
    
    def __init__(self):
        """Initialize the help system"""
        self.help_data = self._load_help_data()
    
    def _load_help_data(self) -> Dict[str, Any]:
        """Load help content and documentation"""
        return {
            'quick_start': {
                'title': '🚀 Quick Start Guide',
                'sections': [
                    {
                        'title': 'Getting Started',
                        'content': [
                            '1. **Select a Persona**: Choose an AI persona from the sidebar to start chatting',
                            '2. **Start a Conversation**: Type your message and press Enter or click Send',
                            '3. **Use Tools**: Access persona-specific tools from the Tools panel',
                            '4. **Manage Sessions**: Create, rename, and delete chat sessions as needed'
                        ]
                    },
                    {
                        'title': 'Keyboard Shortcuts',
                        'content': [
                            '**Ctrl+Enter**: Send message',
                            '**Escape**: Clear input field',
                            '**Tab**: Navigate to tools panel'
                        ]
                    }
                ]
            },
            'personas': {
                'title': '🎭 Understanding Personas',
                'sections': [
                    {
                        'title': 'What are Personas?',
                        'content': [
                            'Personas are AI characters with specific personalities, knowledge, and capabilities.',
                            'Each persona can represent an artist, music analyst, or specialized assistant.',
                            'Personas have unique speaking styles, tool access, and AI configurations.'
                        ]
                    },
                    {
                        'title': 'Artist Personas',
                        'content': [
                            'Artist personas represent real musicians and can manage their own content.',
                            'They have enhanced access to music files, lyrics, and artist-specific tools.',
                            'Artist personas speak authentically and know their music inside out.'
                        ]
                    },
                    {
                        'title': 'Assistant Personas',
                        'content': [
                            'Assistant personas provide specialized help in music analysis and management.',
                            'They can analyze lyrics, compare tracks, and generate reports.',
                            'Each assistant has expertise in specific areas of music.'
                        ]
                    }
                ]
            },
            'tools': {
                'title': '🛠️ Available Tools',
                'sections': [
                    {
                        'title': 'File Operations',
                        'content': [
                            '**Read File**: Access and read music files and documents',
                            '**List Directory**: Browse file structures and folders',
                            '**Search Files**: Find specific files by name or content',
                            '**Read Lyrics**: Access formatted and raw lyrics from tracks'
                        ]
                    },
                    {
                        'title': 'Database Operations',
                        'content': [
                            '**Query Artist Data**: Get information about artists and their work',
                            '**Query Album Data**: Access album details and track listings',
                            '**Query Track Data**: Retrieve track information and metadata',
                            '**Search Music**: Find music by various criteria'
                        ]
                    },
                    {
                        'title': 'Content Operations',
                        'content': [
                            '**Edit Lyrics**: Modify track lyrics (artist personas only)',
                            '**Edit Track Info**: Update track metadata and information',
                            '**Edit Album Info**: Modify album details and descriptions',
                            '**Generate Description**: Create content descriptions using AI'
                        ]
                    },
                    {
                        'title': 'Analysis Operations',
                        'content': [
                            '**Analyze Music**: Get AI-powered music analysis',
                            '**Analyze Lyrics**: Deep dive into lyrical content and themes',
                            '**Compare Tracks**: Side-by-side track comparison',
                            '**Generate Reports**: Create comprehensive music reports'
                        ]
                    }
                ]
            },
            'chat_features': {
                'title': '💬 Chat Features',
                'sections': [
                    {
                        'title': 'Session Management',
                        'content': [
                            '**Create Sessions**: Start new conversations with any persona',
                            '**Rename Sessions**: Give your chats meaningful names',
                            '**Delete Sessions**: Remove old conversations when needed',
                            '**Export Sessions**: Save chat history in JSON or Markdown format'
                        ]
                    },
                    {
                        'title': 'Message Types',
                        'content': [
                            '**User Messages**: Your input and questions',
                            '**Persona Responses**: AI-generated replies from personas',
                            '**Tool Results**: Output from executed tools and commands',
                            '**System Messages**: Important notifications and status updates'
                        ]
                    },
                    {
                        'title': 'Artist-Specific Features',
                        'content': [
                            '**Conversation Starters**: Pre-written prompts for artists',
                            '**Enhanced Tools**: Special access to music management tools',
                            '**Content Validation**: Secure access to artist-owned content',
                            '**Cultural Context**: Genre-specific AI behavior and responses'
                        ]
                    }
                ]
            },
            'troubleshooting': {
                'title': '🔧 Troubleshooting',
                'sections': [
                    {
                        'title': 'Common Issues',
                        'content': [
                            '**No AI Response**: Check if AI service is configured and running',
                            '**Tool Execution Failed**: Verify persona has permission for the tool',
                            '**Session Not Loading**: Refresh the page and try again',
                            '**Permission Denied**: Ensure you\'re using the correct persona for content access'
                        ]
                    },
                    {
                        'title': 'Performance Tips',
                        'content': [
                            '**Limit Message History**: Sessions load faster with fewer messages',
                            '**Use Tool Categories**: Organize tools by category for easier access',
                            '**Clear Old Sessions**: Remove unused sessions to improve performance',
                            '**Restart Browser**: Refresh if the interface becomes unresponsive'
                        ]
                    }
                ]
            },
            'advanced_features': {
                'title': '⚡ Advanced Features',
                'sections': [
                    {
                        'title': 'Persona Customization',
                        'content': [
                            '**Create Custom Personas**: Build your own AI assistants',
                            '**Template System**: Use pre-built templates for common use cases',
                            '**AI Configuration**: Customize temperature, model, and response settings',
                            '**Tool Permissions**: Fine-tune access to specific tools and features'
                        ]
                    },
                    {
                        'title': 'Integration Features',
                        'content': [
                            '**Artist Linking**: Connect personas to existing artist profiles',
                            '**Content Management**: Manage music files and metadata through chat',
                            '**Workflow Automation**: Use tools to automate repetitive tasks',
                            '**Export and Backup**: Save your work in multiple formats'
                        ]
                    }
                ]
            }
        }
    
    def show_help_dialog(self):
        """Show the main help dialog"""
        with ui.dialog() as help_dialog, ui.card().classes('w-full max-w-6xl max-h-[90vh]'):
            # Header
            with ui.row().classes('items-center justify-between mb-6'):
                ui.label('📚 Help & Documentation').classes('text-2xl font-bold text-gray-800')
                ui.button('✕', on_click=help_dialog.close).classes(
                    'w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300'
                )
            
            # Navigation and content
            with ui.row().classes('h-full'):
                # Navigation sidebar
                with ui.column().classes('w-64 border-r border-gray-200 pr-4'):
                    ui.label('Contents').classes('text-lg font-semibold text-gray-700 mb-3')
                    
                    # Navigation buttons
                    for key, section in self.help_data.items():
                        ui.button(
                            section['title'],
                            on_click=lambda k=key: self._show_help_section(k, content_container)
                        ).classes(
                            'w-full text-left p-3 mb-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm'
                        )
                
                # Content area
                with ui.column().classes('flex-1 pl-4 overflow-y-auto') as content_container:
                    # Show quick start by default
                    self._show_help_section('quick_start', content_container)
            
            help_dialog.open()
    
    def _show_help_section(self, section_key: str, content_container):
        """Show a specific help section"""
        if section_key not in self.help_data:
            return
        
        section = self.help_data[section_key]
        content_container.clear()
        
        with content_container:
            # Section title
            ui.label(section['title']).classes('text-xl font-bold text-gray-800 mb-6')
            
            # Section content
            for subsection in section['sections']:
                with ui.card().classes('mb-6 p-4 bg-white border border-gray-200'):
                    ui.label(subsection['title']).classes('text-lg font-semibold text-gray-700 mb-3')
                    
                    with ui.column().classes('space-y-2'):
                        for item in subsection['content']:
                            # Handle markdown-style formatting
                            if item.startswith('**') and '**' in item[2:]:
                                # Bold text
                                parts = item.split('**', 2)
                                with ui.row().classes('items-start'):
                                    ui.label(parts[1]).classes('font-semibold text-gray-800')
                                    if len(parts) > 2:
                                        ui.label(parts[2]).classes('text-gray-600 ml-1')
                            else:
                                ui.label(item).classes('text-gray-600')
    
    def show_context_help(self, context: str):
        """Show context-specific help"""
        help_messages = {
            'persona_creation': 'Create a new AI persona with custom personality and tools',
            'tool_execution': 'Execute tools to analyze music, manage content, or query data',
            'session_management': 'Manage your chat sessions - create, rename, delete, and export',
            'artist_integration': 'Connect personas to artists for enhanced music management',
            'chat_basics': 'Start conversations, send messages, and interact with AI personas'
        }
        
        if context in help_messages:
            ui.notify(f'💡 {help_messages[context]}', type='info', timeout=5000)
    
    def show_tool_help(self, tool_name: str):
        """Show help for a specific tool"""
        tool_help = {
            'read_file': 'Read and display the contents of a file',
            'edit_lyrics': 'Modify track lyrics (requires artist persona permission)',
            'analyze_music': 'Get AI-powered analysis of music content',
            'query_artist_data': 'Retrieve information about artists and their work',
            'export_session': 'Save chat history in JSON or Markdown format'
        }
        
        if tool_name in tool_help:
            with ui.dialog() as tool_help_dialog, ui.card().classes('w-96'):
                ui.label(f'🛠️ {tool_name.replace("_", " ").title()}').classes('text-lg font-bold mb-3')
                ui.label(tool_help[tool_name]).classes('text-gray-600 mb-4')
                ui.button('Got it!', on_click=tool_help_dialog.close).classes(
                    'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded'
                )
                tool_help_dialog.open()
    
    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts help"""
        with ui.dialog() as shortcuts_dialog, ui.card().classes('w-96'):
            ui.label('⌨️ Keyboard Shortcuts').classes('text-lg font-bold mb-4')
            
            shortcuts = [
                ('Ctrl+Enter', 'Send message'),
                ('Escape', 'Clear input field'),
                ('Tab', 'Navigate to tools panel'),
                ('Ctrl+S', 'Save current work'),
                ('Ctrl+Z', 'Undo last action')
            ]
            
            with ui.column().classes('space-y-2'):
                for shortcut, description in shortcuts:
                    with ui.row().classes('justify-between items-center'):
                        ui.label(shortcut).classes('font-mono bg-gray-100 px-2 py-1 rounded text-sm')
                        ui.label(description).classes('text-gray-600 text-sm')
            
            ui.button('Got it!', on_click=shortcuts_dialog.close).classes(
                'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded mt-4'
            )
            
            shortcuts_dialog.open()
    
    def show_quick_tips(self):
        """Show quick tips for better usage"""
        tips = [
            '💡 Use conversation starters to begin engaging conversations with artist personas',
            '💡 Organize your tools by category for easier access and better workflow',
            '💡 Export important chat sessions to keep records of your work',
            '💡 Use keyboard shortcuts to navigate faster and work more efficiently',
            '💡 Check tool permissions before attempting to use them',
            '💡 Rename sessions to keep track of different conversation topics'
        ]
        
        with ui.dialog() as tips_dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('💡 Quick Tips').classes('text-lg font-bold mb-4')
            
            with ui.column().classes('space-y-3'):
                for tip in tips:
                    ui.label(tip).classes('text-gray-600 text-sm')
            
            ui.button('Got it!', on_click=tips_dialog.close).classes(
                'px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded mt-4'
            )
            
            tips_dialog.open()
