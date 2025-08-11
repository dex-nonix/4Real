"""
Database connection and setup
"""
from peewee import SqliteDatabase, Model
from .config import settings

# Create database connection
database = SqliteDatabase(settings.database_path)

class BaseModel(Model):
    """Base model class with database connection"""
    
    class Meta:
        database = database

def init_database():
    """Initialize the database and create tables"""
    database.connect()
    database.create_tables([
        Artist, Album, Track, Style, 
        TrackStyle, RhymeTechnique, TrackRhymeTechnique,
        RhymeTechniqueGenre, RhymeTechniqueArtist,
        # Chat system models
        AIPersona, ChatSession, ChatMessage
    ], safe=True)
    database.close()

def get_database():
    """Get database connection"""
    return database

# Import models here to avoid circular imports
from .models import (
    Artist, Album, Track, Style, TrackStyle, 
    RhymeTechnique, TrackRhymeTechnique, RhymeTechniqueGenre, RhymeTechniqueArtist,
    # Chat system models
    AIPersona, ChatSession, ChatMessage
)
