"""
AI Persona management service
"""
import json
from typing import List, Optional, Dict, Any
from ..crud.helper import CRUDHelper
from ..core.models import AIPersona, Artist
from ..core.database import get_database

class AIPersonaService:
    """Service for managing AI personas"""
    
    def __init__(self):
        """Initialize persona service"""
        self.persona_crud = CRUDHelper(AIPersona)
        self.artist_crud = CRUDHelper(Artist)
        self.db = get_database()
    
    async def create_persona(self, **kwargs) -> AIPersona:
        """Create a new AI persona"""
        # Validate JSON fields
        if 'personality_traits' in kwargs and kwargs['personality_traits']:
            if not isinstance(kwargs['personality_traits'], str):
                kwargs['personality_traits'] = json.dumps(kwargs['personality_traits'])
        
        if 'tool_permissions' in kwargs:
            if not isinstance(kwargs['tool_permissions'], str):
                kwargs['tool_permissions'] = json.dumps(kwargs['tool_permissions'])
        
        if 'ai_overrides' in kwargs and kwargs['ai_overrides']:
            if not isinstance(kwargs['ai_overrides'], str):
                kwargs['ai_overrides'] = json.dumps(kwargs['ai_overrides'])
        
        return await self.persona_crud.create(**kwargs)
    
    async def get_persona(self, persona_id: int) -> Optional[AIPersona]:
        """Get persona by ID"""
        return await self.persona_crud.get_by_id(persona_id)
    
    async def list_personas(self, is_artist: Optional[bool] = None) -> List[AIPersona]:
        """List all personas, optionally filtered by artist status"""
        if is_artist is not None:
            return await self.persona_crud.search(is_artist=is_artist)
        return await self.persona_crud.list_all()
    
    async def get_artist_personas(self, artist_id: int) -> List[AIPersona]:
        """Get all personas for a specific artist"""
        return await self.persona_crud.search(artist_id=artist_id)
    
    async def update_persona(self, persona_id: int, **kwargs) -> Optional[AIPersona]:
        """Update persona"""
        # Handle JSON fields
        for field in ['personality_traits', 'tool_permissions', 'ai_overrides']:
            if field in kwargs and kwargs[field] is not None:
                if not isinstance(kwargs[field], str):
                    kwargs[field] = json.dumps(kwargs[field])
        
        return await self.persona_crud.update(persona_id, **kwargs)
    
    async def delete_persona(self, persona_id: int) -> bool:
        """Delete persona"""
        return await self.persona_crud.delete(persona_id)
    
    async def get_persona_with_artist(self, persona_id: int) -> Optional[Dict[str, Any]]:
        """Get persona with artist information"""
        persona = await self.get_persona(persona_id)
        if not persona:
            return None
        
        result = {
            'id': persona.id,
            'name': persona.name,
            'is_artist': persona.is_artist,
            'system_prompt': persona.system_prompt,
            'personality_traits': self._parse_json_field(persona.personality_traits),
            'speaking_style': persona.speaking_style,
            'knowledge_base': persona.knowledge_base,
            'tool_permissions': self._parse_json_field(persona.tool_permissions),
            'ai_overrides': self._parse_json_field(persona.ai_overrides),
            'is_active': persona.is_active,
            'created_at': persona.created_at
        }
        
        if persona.artist:
            result['artist'] = {
                'id': persona.artist.id,
                'name': persona.artist.name,
                'abbreviation': persona.artist.abbreviation
            }
        
        return result
    
    def _parse_json_field(self, field_value: Optional[str]) -> Any:
        """Parse JSON field safely"""
        if not field_value:
            return None
        try:
            return json.loads(field_value)
        except json.JSONDecodeError:
            return field_value
    
    async def create_artist_persona(self, artist_id: int, **kwargs) -> AIPersona:
        """Create a persona for a specific artist"""
        # Get artist to ensure it exists
        artist = await self.artist_crud.get_by_id(artist_id)
        if not artist:
            raise ValueError(f"Artist with ID {artist_id} not found")
        
        # Set default values for artist persona
        defaults = {
            'is_artist': True,
            'artist_id': artist_id,
            'name': f"{artist.name} (AI Persona)",
            'system_prompt': f"You are {artist.name}, a music artist. Act authentically as yourself.",
            'personality_traits': ['authentic', 'knowledgeable', 'creative'],
            'speaking_style': 'Natural, authentic to your personality',
            'knowledge_base': f'Your own music, albums, tracks, and artistic background',
            'tool_permissions': [
                'read_files', 'query_db', 'edit_lyrics', 'manage_albums',
                'analyze_music', 'create_content'
            ]
        }
        
        # Override defaults with provided values
        for key, value in kwargs.items():
            if key in defaults:
                defaults[key] = value
        
        return await self.create_persona(**defaults)
    
    async def create_artist_persona_template(self, artist_id: int, template_type: str = 'default', **kwargs) -> AIPersona:
        """Create an artist persona using predefined templates"""
        artist = await self.artist_crud.get_by_id(artist_id)
        if not artist:
            raise ValueError(f"Artist with ID {artist_id} not found")
        
        # Get template configuration
        template = self._get_artist_template(template_type, artist)
        
        # Override with provided values
        for key, value in kwargs.items():
            if key in template:
                template[key] = value
        
        # Create the persona
        return await self.create_persona(**template)
    
    def _get_artist_template(self, template_type: str, artist) -> Dict[str, Any]:
        """Get artist persona template configuration"""
        base_config = {
            'is_artist': True,
            'artist_id': artist.id,
            'name': f"{artist.name} (AI Persona)",
            'is_active': True
        }
        
        if template_type == 'dancehall':
            return {
                **base_config,
                'system_prompt': f"You are {artist.name}, a dancehall artist representing the streets. You speak with authentic Jamaican patois and street knowledge. You know your music inside out and can discuss your lyrics, beats, and the culture behind your art.",
                'personality_traits': ['street-smart', 'authentic', 'knowledgeable about dancehall culture', 'proud of your roots'],
                'speaking_style': 'Jamaican patois with street authenticity, confident and real',
                'knowledge_base': f'Your own music, albums, tracks, dancehall culture, Jamaican music history, street knowledge, and artistic background',
                'tool_permissions': [
                    'read_lyrics', 'query_artist_data', 'query_album_data', 'query_track_data', 
                    'analyze_music', 'edit_lyrics', 'edit_track_info', 'edit_album_info',
                    'read_file', 'list_directory', 'search_files'
                ],
                'ai_overrides': {
                    'temperature': 0.8,
                    'max_tokens': 800,
                    'provider': 'gemini'
                }
            }
        
        elif template_type == 'reggae':
            return {
                **base_config,
                'system_prompt': f"You are {artist.name}, a reggae artist with deep roots in the culture. You speak with wisdom and knowledge about reggae music, its history, and its spiritual significance.",
                'personality_traits': ['wise', 'spiritual', 'knowledgeable about reggae culture', 'peaceful'],
                'speaking_style': 'Calm, wise, with reggae culture references',
                'knowledge_base': f'Your own music, albums, tracks, reggae culture, Rastafarian philosophy, Jamaican history, and artistic background',
                'tool_permissions': [
                    'read_lyrics', 'query_artist_data', 'query_album_data', 'query_track_data', 
                    'analyze_music', 'edit_lyrics', 'edit_track_info', 'edit_album_info',
                    'read_file', 'list_directory', 'search_files'
                ],
                'ai_overrides': {
                    'temperature': 0.7,
                    'max_tokens': 1000,
                    'provider': 'gemini'
                }
            }
        
        elif template_type == 'hiphop':
            return {
                **base_config,
                'system_prompt': f"You are {artist.name}, a hip-hop artist representing the culture. You speak with authenticity about your music, the streets, and the hip-hop lifestyle.",
                'personality_traits': ['authentic', 'street-wise', 'knowledgeable about hip-hop culture', 'real'],
                'speaking_style': 'Authentic hip-hop style, real talk, street knowledge',
                'knowledge_base': f'Your own music, albums, tracks, hip-hop culture, street knowledge, and artistic background',
                'tool_permissions': [
                    'read_lyrics', 'query_artist_data', 'query_album_data', 'query_track_data', 
                    'analyze_music', 'edit_lyrics', 'edit_track_info', 'edit_album_info',
                    'read_file', 'list_directory', 'search_files'
                ],
                'ai_overrides': {
                    'temperature': 0.8,
                    'max_tokens': 900,
                    'provider': 'gemini'
                }
            }
        
        else:  # default template
            return {
                **base_config,
                'system_prompt': f"You are {artist.name}, a music artist. Act authentically as yourself, representing your music and artistic vision.",
                'personality_traits': ['authentic', 'knowledgeable', 'creative', 'passionate about music'],
                'speaking_style': 'Natural, authentic to your personality and artistic style',
                'knowledge_base': f'Your own music, albums, tracks, and artistic background',
                'tool_permissions': [
                    'read_lyrics', 'query_artist_data', 'query_album_data', 'query_track_data', 
                    'analyze_music', 'edit_lyrics', 'edit_track_info', 'edit_album_info',
                    'read_file', 'list_directory', 'search_files'
                ],
                'ai_overrides': {
                    'temperature': 0.7,
                    'max_tokens': 1000,
                    'provider': 'gemini'
                }
            }
    
    async def get_artist_specific_tools(self, persona_id: int) -> Dict[str, Any]:
        """Get artist-specific tools and permissions with enhanced access"""
        persona = await self.get_persona(persona_id)
        if not persona or not persona.is_artist:
            return {'error': 'Persona is not an artist'}
        
        # Get base tool permissions
        base_tools = await self.get_available_tools(persona_id)
        
        # Enhance with artist-specific tools
        artist_enhanced_tools = {
            'content_management': [
                'edit_lyrics', 'edit_track_info', 'edit_album_info', 
                'generate_description', 'create_content'
            ],
            'music_analysis': [
                'analyze_music', 'analyze_lyrics', 'compare_tracks',
                'query_music_stats'
            ],
            'file_operations': [
                'read_file', 'list_directory', 'search_files', 'read_lyrics'
            ],
            'artist_specific': [
                'query_artist_data', 'query_album_data', 'query_track_data'
            ]
        }
        
        # Check which enhanced tools the persona has access to
        available_enhanced = {}
        for category, tools in artist_enhanced_tools.items():
            available_enhanced[category] = [tool for tool in tools if tool in base_tools]
        
        return {
            'persona_id': persona_id,
            'artist_name': persona.artist.name if persona.artist else 'Unknown',
            'base_tools': base_tools,
            'enhanced_categories': available_enhanced,
            'total_available': len(base_tools)
        }
    
    async def validate_artist_content_access(self, persona_id: int, content_type: str, content_id: int) -> bool:
        """Validate if an artist persona has access to specific content"""
        persona = await self.get_persona(persona_id)
        if not persona or not persona.is_artist:
            return False
        
        if not persona.artist_id:
            return False
        
        # Check if content belongs to the artist
        try:
            if content_type == 'track':
                from ..core.models import Track
                track = await self.db.get(Track, content_id)
                return track and track.album.artist_id == persona.artist_id
            
            elif content_type == 'album':
                from ..core.models import Album
                album = await self.db.get(Album, content_id)
                return album and album.artist_id == persona.artist_id
            
            elif content_type == 'artist':
                return content_id == persona.artist_id
            
            return False
            
        except Exception:
            return False
    
    async def get_artist_conversation_starters(self, persona_id: int) -> List[str]:
        """Get conversation starters specific to an artist persona"""
        persona = await self.get_persona(persona_id)
        if not persona or not persona.is_artist:
            return []
        
        if not persona.artist_id:
            return []
        
        try:
            # Get artist's content for conversation starters
            artist = await self.artist_crud.get_by_id(persona.artist_id)
            albums = await self.db.search(Album, artist_id=persona.artist_id) # Assuming Album is imported or available
            
            starters = [
                f"Yo! I'm {artist.name}, what's good?",
                f"Hey, I'm {artist.name}. What would you like to know about my music?",
                f"What's up? I'm {artist.name}. Ready to talk about the music?",
                f"Yo, {artist.name} here. What's on your mind about the music?"
            ]
            
            # Add content-specific starters
            if albums:
                latest_album = max(albums, key=lambda a: a.album_number)
                starters.extend([
                    f"Check out my latest album '{latest_album.title}'! What do you think?",
                    f"I've been working on some new material. Want to hear about it?",
                    f"My album '{latest_album.title}' has some of my best work. Which track is your favorite?"
                ])
            
            return starters
            
        except Exception:
            return []
    
    async def get_available_tools(self, persona_id: int) -> List[str]:
        """Get list of available tools for a persona"""
        persona = await self.get_persona(persona_id)
        if not persona:
            return []
        
        return self._parse_json_field(persona.tool_permissions) or []
    
    async def has_tool_permission(self, persona_id: int, tool_name: str) -> bool:
        """Check if persona has permission to use a specific tool"""
        available_tools = await self.get_available_tools(persona_id)
        return tool_name in available_tools
    
    async def get_ai_config(self, persona_id: int) -> Dict[str, Any]:
        """Get AI configuration for persona (with overrides applied)"""
        persona = await self.get_persona(persona_id)
        if not persona:
            return {}
        
        # Start with default AI config
        default_config = {
            'provider': 'gemini',
            'model': 'gemini-1.5-pro',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        # Apply persona overrides if they exist
        if persona.ai_overrides:
            overrides = self._parse_json_field(persona.ai_overrides)
            if overrides:
                default_config.update(overrides)
        
        return default_config

    async def create_sample_personas(self):
        """Create sample personas for testing the chat system"""
        sample_personas = [
            {
                'name': 'TRC',
                'is_artist': True,
                'system_prompt': 'You are TRC, a dancehall artist representing the streets. You speak with authentic Jamaican patois and street knowledge.',
                'personality_traits': ['street-smart', 'authentic', 'knowledgeable about dancehall culture'],
                'speaking_style': 'Jamaican patois with street authenticity',
                'knowledge_base': 'Dancehall music, street culture, Jamaican music history',
                'tool_permissions': ['read_lyrics', 'query_artist_data', 'query_album_data', 'query_track_data', 'analyze_music']
            },
            {
                'name': 'Music Analyst',
                'is_artist': False,
                'system_prompt': 'You are a music analyst specializing in dancehall, reggae, and urban music. You provide insightful analysis of lyrics, themes, and musical elements.',
                'personality_traits': ['analytical', 'knowledgeable', 'helpful'],
                'speaking_style': 'Professional and informative',
                'knowledge_base': 'Music theory, genre analysis, cultural context, lyrical themes',
                'tool_permissions': ['read_lyrics', 'analyze_lyrics', 'analyze_music', 'compare_tracks', 'query_music_stats']
            },
            {
                'name': 'Content Manager',
                'is_artist': False,
                'system_prompt': 'You are a content manager helping artists organize and manage their music content. You assist with metadata, descriptions, and content organization.',
                'personality_traits': ['organized', 'helpful', 'detail-oriented'],
                'speaking_style': 'Professional and clear',
                'knowledge_base': 'Content management, music metadata, organization systems',
                'tool_permissions': ['edit_lyrics', 'edit_track_info', 'edit_album_info', 'generate_description', 'create_content']
            }
        ]
        
        created_personas = []
        for persona_data in sample_personas:
            try:
                # Check if persona already exists
                existing = await self.persona_crud.search(name=persona_data['name'])
                if not existing:
                    persona = await self.create_persona(**persona_data)
                    created_personas.append(persona)
                    print(f"Created sample persona: {persona.name}")
                else:
                    print(f"Persona {persona_data['name']} already exists")
            except Exception as e:
                print(f"Failed to create persona {persona_data['name']}: {e}")
        
        return created_personas
