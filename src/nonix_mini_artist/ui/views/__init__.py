"""
UI Views module
"""

from .artists_view import ArtistsView
from .albums_view import AlbumsView
from .tracks_view import TracksView
from .styles_view import StylesView
from .ai_settings_view import AISettingsView
from .chat_view import ChatView
from .persona_management_view import PersonaManagementView

__all__ = [
    'ArtistsView',
    'AlbumsView', 
    'TracksView',
    'StylesView',
    'AISettingsView',
    'ChatView',
    'PersonaManagementView'
]
