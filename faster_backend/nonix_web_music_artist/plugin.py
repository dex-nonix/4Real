from nonix_web.plugin.base_plugin import BasePlugin, routers
from nonix_web.utils.di import di_register

from nonix_web_agentic.llm.llm_tools_decorator import llm_tools
from .llm_tools.album_tools import album_tool_service
from .llm_tools.track_tools import track_tool_service
from .llm_tools.artist_tools import artist_tool_service
from .llm_tools.style_tools import style_tool_service
from .llm_tools.lyric_tools import lyric_tool_service
from .routers.album import AlbumRouter
from .routers.artist import ArtistRouter
from .routers.rhyme_technique import RhymeTechniqueRouter
from .routers.style import StyleRouter
from .routers.track import TrackRouter
from .services.album_service import AlbumService
from .services.artist_service import ArtistService
from .services.track_service import TrackService
from .services.style_service import StyleService
from .services.rhyme_technique_service import RhymeTechniqueService


@routers([
    AlbumRouter,
    ArtistRouter,
    RhymeTechniqueRouter,
    StyleRouter,
    TrackRouter
])
@llm_tools([
    # Enhanced CRUD Tools with Relationship Management
    album_tool_service,  # Album CRUD + track management
    track_tool_service,  # Track CRUD + positioning
    artist_tool_service,  # Artist CRUD + catalog
    style_tool_service,  # Style CRUD + track assignment
    lyric_tool_service,  # Lyrics management
])
class NxWebMusicArtistPlugin(BasePlugin):

    def _configure(self, server, config):
        """Register services in DI system"""
        di_register(AlbumService)
        di_register(ArtistService)
        di_register(TrackService)
        di_register(StyleService)
        di_register(RhymeTechniqueService)
