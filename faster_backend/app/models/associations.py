from __future__ import annotations

from ..database import Base

TrackStyle = Table(
    'track_styles',
    Column('track_id', Integer, ForeignKey('tracks.id'), primary_key=True),
    Column('style_id', Integer, ForeignKey('styles.id'), primary_key=True),
)

TrackRhymeTechnique = Table(
    'track_rhyme_techniques',
    Column('track_id', Integer, ForeignKey('tracks.id'), primary_key=True),
    Column('rhyme_technique_id', Integer, ForeignKey('rhyme_techniques.id'), primary_key=True),
)
