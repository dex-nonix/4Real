"""
Chat session and message management service
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..crud.helper import CRUDHelper
from ..core.models import ChatSession, ChatMessage, AIPersona
from ..core.database import get_database
from ..ai.service import AIService

class ChatService:
    """Service for managing chat sessions and messages"""
    
    def __init__(self):
        """Initialize chat service"""
        self.session_crud = CRUDHelper(ChatSession)
        self.message_crud = CRUDHelper(ChatMessage)
        self.persona_crud = CRUDHelper(AIPersona)
        self.db = get_database()
        self.ai_service = AIService()
    
    async def create_session(self, persona_id: int, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session with a persona"""
        # Get persona to ensure it exists
        persona = await self.persona_crud.get_by_id(persona_id)
        if not persona:
            raise ValueError(f"Persona with ID {persona_id} not found")
        
        # Generate default title if not provided
        if not title:
            title = f"Chat with {persona.name}"
        
        session = await self.session_crud.create(
            persona_id=persona_id,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return session
    
    async def get_session(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID"""
        return await self.session_crud.get_by_id(session_id)
    
    async def get_active_sessions(self, persona_id: Optional[int] = None) -> List[ChatSession]:
        """Get active chat sessions, optionally filtered by persona"""
        if persona_id:
            return await self.session_crud.search(persona_id=persona_id, is_active=True)
        return await self.session_crud.search(is_active=True)
    
    async def close_session(self, session_id: int) -> bool:
        """Close a chat session"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        return await self.session_crud.update(session_id, is_active=False)
    
    async def delete_session(self, session_id: int) -> bool:
        """Delete a chat session and all its messages"""
        return await self.session_crud.delete(session_id)
    
    async def add_message(self, session_id: int, sender_type: str, content: str, 
                         message_type: str = 'text', tool_info: Optional[Dict[str, Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Add a message to a chat session"""
        # Validate session exists
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        
        # Prepare message data
        message_data = {
            'session_id': session_id,
            'sender_type': sender_type,
            'content': content,
            'message_type': message_type,
            'timestamp': datetime.now()
        }
        
        # Add tool information if provided
        if tool_info:
            message_data.update({
                'tool_used': tool_info.get('tool_name'),
                'tool_result': tool_info.get('result'),
                'tool_status': tool_info.get('status', 'success')
            })
        
        # Add metadata if provided
        if metadata:
            message_data['metadata'] = json.dumps(metadata)
        
        # Create message
        message = await self.message_crud.create(**message_data)
        
        # Update session metadata
        await self._update_session_metadata(session_id, sender_type, content)
        
        return message
    
    async def get_session_messages(self, session_id: int, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get messages for a chat session"""
        try:
            self.db.connect()
            query = ChatMessage.select().where(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp)
            if limit:
                query = query.limit(limit)
            return list(query)
        finally:
            self.db.close()
    
    async def get_session_history(self, session_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get formatted session history"""
        messages = await self.get_session_messages(session_id, limit)
        
        history = []
        for message in messages:
            message_data = {
                'id': message.id,
                'sender_type': message.sender_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'message_type': message.message_type
            }
            
            # Add tool information if present
            if message.tool_used:
                message_data.update({
                    'tool_used': message.tool_used,
                    'tool_result': message.tool_result,
                    'tool_status': message.tool_status
                })
            
            # Add metadata if present
            if message.metadata:
                try:
                    message_data['metadata'] = json.loads(message.metadata)
                except json.JSONDecodeError:
                    message_data['metadata'] = message.metadata
            
            history.append(message_data)
        
        return history
    
    async def search_messages(self, session_id: int, query: str) -> List[ChatMessage]:
        """Search messages in a session"""
        try:
            self.db.connect()
            return list(ChatMessage.select().where(
                (ChatMessage.session_id == session_id) & 
                (ChatMessage.content.contains(query))
            ).order_by(ChatMessage.timestamp))
        finally:
            self.db.close()
    
    async def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """Get statistics for a chat session"""
        session = await self.get_session(session_id)
        if not session:
            return {}
        
        messages = await self.get_session_messages(session_id)
        
        # Count messages by sender type
        sender_counts = {}
        tool_usage = {}
        
        for message in messages:
            # Count by sender
            sender_type = message.sender_type
            sender_counts[sender_type] = sender_counts.get(sender_type, 0) + 1
            
            # Count tool usage
            if message.tool_used:
                tool_name = message.tool_used
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        return {
            'session_id': session_id,
            'title': session.title,
            'persona_name': session.persona.name,
            'total_messages': len(messages),
            'sender_counts': sender_counts,
            'tool_usage': tool_usage,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.updated_at.isoformat(),
            'is_active': session.is_active
        }
    
    async def _update_session_metadata(self, session_id: int, sender_type: str, content: str):
        """Update session metadata (last message, total count, etc.)"""
        session = await self.get_session(session_id)
        if not session:
            return
        
        # Update last message based on sender type
        if sender_type == 'user':
            await self.session_crud.update(session_id, 
                                         last_user_message=content,
                                         updated_at=datetime.now())
        elif sender_type == 'persona':
            await self.session_crud.update(session_id,
                                         last_persona_response=content,
                                         updated_at=datetime.now())
        
        # Update total message count
        messages = await self.get_session_messages(session_id)
        await self.session_crud.update(session_id, total_messages=len(messages))
    
    async def export_session(self, session_id: int, format: str = 'json') -> str:
        """Export chat session in specified format"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        
        history = await self.get_session_history(session_id)
        session_data = {
            'session': {
                'id': session.id,
                'title': session.title,
                'persona_name': session.persona.name,
                'created_at': session.created_at.isoformat(),
                'total_messages': session.total_messages
            },
            'messages': history
        }
        
        if format.lower() == 'json':
            return json.dumps(session_data, indent=2)
        elif format.lower() == 'markdown':
            return self._format_as_markdown(session_data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _format_as_markdown(self, session_data: Dict[str, Any]) -> str:
        """Format session data as markdown"""
        session = session_data['session']
        messages = session_data['messages']
        
        md = f"# Chat Session: {session['title']}\n\n"
        md += f"**Persona**: {session['persona_name']}\n"
        md += f"**Created**: {session['created_at']}\n"
        md += f"**Total Messages**: {session['total_messages']}\n\n"
        md += "---\n\n"
        
        for message in messages:
            timestamp = message['timestamp']
            sender = message['sender_type'].title()
            content = message['content']
            
            md += f"**{timestamp} - {sender}**: {content}\n\n"
            
            # Add tool information if present
            if message.get('tool_used'):
                md += f"*Tool: {message['tool_used']} ({message['tool_status']})*\n\n"
        
        return md

    async def generate_ai_response(self, session_id: int, user_message: str) -> Optional[ChatMessage]:
        """Generate AI response for a user message using the persona's configuration"""
        try:
            # Get the session and persona
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session with ID {session_id} not found")
            
            persona = await self.persona_crud.get_by_id(session.persona_id) # Use persona_crud for persona
            if not persona:
                raise ValueError(f"Persona not found for session {session_id}")
            
            # Prepare AI request context
            context = {
                'persona_name': persona.name,
                'persona_traits': persona.personality_traits,
                'speaking_style': persona.speaking_style,
                'knowledge_base': persona.knowledge_base,
                'is_artist': persona.is_artist,
                'artist_name': persona.artist.name if persona.artist else None,
                'artist_abbreviation': persona.artist.abbreviation if persona.artist else ''
            }
            
            # Create system prompt for the persona
            system_prompt = self._create_persona_system_prompt(persona, context)
            
            # Get conversation history for context
            history = await self.get_session_history(session_id, limit=10)
            conversation_context = self._format_conversation_context(history, user_message)
            
            # Generate AI response
            ai_response = await self._call_ai_service(system_prompt, conversation_context, context)
            
            if ai_response:
                # Add the AI response to the chat
                message = await self.add_message(
                    session_id=session_id,
                    sender_type='persona',
                    content=ai_response,
                    message_type='text',
                    metadata={'ai_generated': True, 'persona_id': persona.id}
                )
                return message
            
        except Exception as e:
            print(f"Failed to generate AI response: {e}")
            # Add error message to chat
            error_message = f"Sorry, I encountered an error while processing your message. Please try again."
            return await self.add_message(
                session_id=session_id,
                sender_type='persona',
                content=error_message,
                message_type='system',
                metadata={'error': str(e), 'ai_generated': False}
            )
        
        return None
    
    def _create_persona_system_prompt(self, persona: AIPersona, context: Dict[str, Any]) -> str:
        """Create a system prompt for the AI based on persona configuration"""
        prompt_parts = []
        
        # Base persona identity
        if context['is_artist']:
            prompt_parts.append(f"You are {persona.name}, a music artist.")
            if context.get('artist_name'):
                prompt_parts.append(f"You are specifically representing the artist {context['artist_name']}.")
        else:
            prompt_parts.append(f"You are {persona.name}, an AI assistant.")
        
        # Add personality traits
        if context.get('personality_traits'):
            traits = context['personality_traits']
            if isinstance(traits, list):
                prompt_parts.append(f"Your personality traits include: {', '.join(traits)}")
            else:
                prompt_parts.append(f"Your personality: {traits}")
        
        # Add speaking style
        if context.get('speaking_style'):
            prompt_parts.append(f"Your speaking style: {context['speaking_style']}")
        
        # Add knowledge base
        if context.get('knowledge_base'):
            prompt_parts.append(f"Your expertise includes: {context['knowledge_base']}")
        
        # Add core instructions
        prompt_parts.append("You are having a conversation with a user. Respond naturally and helpfully based on your persona.")
        prompt_parts.append("Keep responses conversational and engaging. Use your personality and knowledge to provide valuable insights.")
        
        return " ".join(prompt_parts)
    
    def _format_conversation_context(self, history: List[Dict[str, Any]], current_message: str) -> str:
        """Format conversation history for AI context"""
        if not history:
            return f"User: {current_message}"
        
        # Format recent conversation history
        context_parts = []
        for msg in history[-5:]:  # Last 5 messages for context
            sender = "User" if msg['sender_type'] == 'user' else "You"
            context_parts.append(f"{sender}: {msg['content']}")
        
        context_parts.append(f"User: {current_message}")
        return "\n".join(context_parts)
    
    async def _call_ai_service(self, system_prompt: str, conversation_context: str, context: Dict[str, Any]) -> Optional[str]:
        """Call the AI service to generate a response"""
        try:
            # Create a custom preset for this persona
            from ..ai.models import AIPreset
            
            # Use default Gemini provider for now
            preset = AIPreset(
                name=f"persona_{context.get('persona_name', 'unknown')}",
                provider="gemini",
                model="gemini-1.5-pro",
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            # Add the preset temporarily
            self.ai_service.add_preset(preset)
            
            # Create analysis request
            from ..ai.models import AIAnalysisRequest
            request = AIAnalysisRequest(
                preset_name=preset.name,
                content=conversation_context,
                context=context
            )
            
            # Generate response
            response = await self.ai_service.analyze(request)
            
            # Clean up temporary preset
            self.ai_service.delete_preset(preset.name)
            
            if response.success:
                return response.content
            else:
                print(f"AI service error: {response.error}")
                return None
                
        except Exception as e:
            print(f"Error calling AI service: {e}")
            return None

    async def get_artist_conversation_starters(self, session_id: int) -> List[str]:
        """Get conversation starters for artist personas"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return []
            
            return await self.persona_crud.get_artist_conversation_starters(session.persona_id)
            
        except Exception as e:
            print(f"Failed to get conversation starters: {e}")
            return []
    
    async def get_artist_specific_tools(self, session_id: int) -> Dict[str, Any]:
        """Get artist-specific tools and permissions for the current session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return {'error': 'Session not found'}
            
            return await self.persona_crud.get_artist_specific_tools(session.persona_id)
            
        except Exception as e:
            print(f"Failed to get artist tools: {e}")
            return {'error': str(e)}
