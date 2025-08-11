"""
Database models for the music metadata system
"""
from datetime import datetime
from peewee import *
from .database import BaseModel

class Artist(BaseModel):
    """Artist model"""
    name = CharField(unique=True, max_length=255)
    abbreviation = CharField(max_length=50, null=True)
    persona = TextField(null=True)
    image_path = CharField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.now)
    
    def __str__(self):
        return self.name

class Album(BaseModel):
    """Album model"""
    artist = ForeignKeyField(Artist, backref='albums', on_delete='CASCADE')
    album_number = IntegerField()
    title = CharField(max_length=255)
    description = TextField(null=True)
    cover_path = CharField(max_length=500, null=True)
    release_date = DateField(null=True)
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"

class Track(BaseModel):
    """Track model"""
    album = ForeignKeyField(Album, backref='tracks', on_delete='CASCADE')
    track_number = IntegerField()
    name = CharField(max_length=255)
    raw_lyrics = TextField(null=True)
    formatted_lyrics = TextField(null=True)
    duration = IntegerField(null=True)  # in seconds
    
    def __str__(self):
        return f"{self.track_number}. {self.name}"

class Style(BaseModel):
    """Musical style/genre model"""
    name = CharField(unique=True, max_length=100)
    category = CharField(max_length=50, null=True)
    description = TextField(null=True)
    
    def __str__(self):
        return self.name

class TrackStyle(BaseModel):
    """Junction table for Track-Style M:N relationship"""
    track = ForeignKeyField(Track, backref='track_styles', on_delete='CASCADE')
    style = ForeignKeyField(Style, backref='track_styles', on_delete='CASCADE')
    is_included = BooleanField(default=True)  # True for includes, False for excludes
    
    class Meta:
        indexes = (
            (('track', 'style'), True),  # Unique constraint
        )

class RhymeTechnique(BaseModel):
    """Rhyme technique model"""
    name = CharField(unique=True, max_length=100)
    category = CharField(max_length=50)  # rhyme-types, rhyme-patterns, etc.
    description = TextField(null=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class TrackRhymeTechnique(BaseModel):
    """Junction table for Track-RhymeTechnique M:N relationship"""
    track = ForeignKeyField(Track, backref='track_rhyme_techniques', on_delete='CASCADE')
    rhyme_technique = ForeignKeyField(RhymeTechnique, backref='track_rhyme_techniques', on_delete='CASCADE')
    
    class Meta:
        indexes = (
            (('track', 'rhyme_technique'), True),  # Unique constraint
        )

class RhymeTechniqueGenre(BaseModel):
    """Genre weights for rhyme techniques"""
    rhyme_technique = ForeignKeyField(RhymeTechnique, backref='genre_weights', on_delete='CASCADE')
    genre = CharField(max_length=100)
    weight = FloatField(default=1.0)
    
    class Meta:
        indexes = (
            (('rhyme_technique', 'genre'), True),  # Unique constraint
        )

class RhymeTechniqueArtist(BaseModel):
    """Artist weights for rhyme techniques"""
    rhyme_technique = ForeignKeyField(RhymeTechnique, backref='artist_weights', on_delete='CASCADE')
    artist = CharField(max_length=255)
    weight = FloatField(default=1.0)
    
    class Meta:
        indexes = (
            (('rhyme_technique', 'artist'), True),  # Unique constraint
        )

# ============================================================================
# CHAT SYSTEM MODELS
# ============================================================================

class AIPersona(BaseModel):
    """AI persona that can optionally be an artist"""
    name = CharField(max_length=255)
    is_artist = BooleanField(default=False)
    artist = ForeignKeyField(Artist, backref='personas', null=True)
    
    # Core personality
    system_prompt = TextField()
    personality_traits = TextField(null=True)  # JSON array
    speaking_style = TextField(null=True)
    
    # Knowledge and capabilities
    knowledge_base = TextField(null=True)
    tool_permissions = TextField()  # JSON array of allowed tools
    
    # Optional AI configuration overrides
    ai_overrides = TextField(null=True)  # JSON with any AI settings to override
    
    # Status
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    
    def __str__(self):
        return f"{self.name} ({'Artist' if self.is_artist else 'Assistant'})"

class ChatSession(BaseModel):
    """Individual chat session with a persona"""
    persona = ForeignKeyField(AIPersona, backref='chat_sessions', on_delete='CASCADE')
    title = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    is_active = BooleanField(default=True)
    
    # Chat metadata
    total_messages = IntegerField(default=0)
    last_user_message = TextField(null=True)
    last_persona_response = TextField(null=True)
    
    def __str__(self):
        return f"Chat: {self.title} with {self.persona.name}"

class ChatMessage(BaseModel):
    """Individual message in a chat session"""
    session = ForeignKeyField(ChatSession, backref='messages', on_delete='CASCADE')
    sender_type = CharField(max_length=50)  # 'user', 'persona', 'tool_result'
    content = TextField()
    timestamp = DateTimeField(default=datetime.now)
    
    # Tool execution info
    tool_used = CharField(max_length=100, null=True)
    tool_result = TextField(null=True)
    tool_status = CharField(max_length=50, null=True)  # 'success', 'error', 'pending'
    
    # Message metadata
    message_type = CharField(max_length=50)  # 'text', 'tool_result', 'system'
    metadata = TextField(null=True)  # JSON for additional data
    
    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}..."
