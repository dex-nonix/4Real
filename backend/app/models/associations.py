from __future__ import annotations

from .. import db

TrackStyle = db.Table(
    'track_styles',
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'), primary_key=True),
    db.Column('style_id', db.Integer, db.ForeignKey('styles.id'), primary_key=True),
)

TrackRhymeTechnique = db.Table(
    'track_rhyme_techniques',
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'), primary_key=True),
    db.Column('rhyme_technique_id', db.Integer, db.ForeignKey('rhyme_techniques.id'), primary_key=True),
)
