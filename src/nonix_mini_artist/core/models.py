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
