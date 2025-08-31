from nonix_web.plugin.base_plugin import BasePlugin, api_services

from nonix_web_agentic.llm.llm_tools_decorator import llm_tools
from .llm_tools.album_tools import album_tool_service
from .llm_tools.track_tools import track_tool_service
from .llm_tools.artist_tools import artist_tool_service
from .llm_tools.style_tools import style_tool_service
from .llm_tools.track_style_tools import track_style_tool_service
from .llm_tools.lyric_tools import lyric_tool_service
from .services.album import AlbumService
from .services.artist import ArtistService
from .services.rhyme_technique import RhymeTechniqueService
from .services.style import StyleService
from .services.track import TrackService


@api_services([
    AlbumService,
    ArtistService,
    RhymeTechniqueService,
    StyleService,
    TrackService
])
@llm_tools([
    # Class-based CRUD Tools
    album_tool_service,  # Album CRUD operations
    track_tool_service,  # Track CRUD operations
    artist_tool_service,  # Artist CRUD operations
    style_tool_service,  # Style management operations
    track_style_tool_service,  # Track-Style relationship management
    lyric_tool_service,  # Lyrics management operations
])
class NxWebMusicArtistPlugin(BasePlugin):
    pass
