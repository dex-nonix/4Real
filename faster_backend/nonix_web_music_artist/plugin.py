from nonix_web.plugin.base_plugin import BasePlugin, api_services

from nonix_web_agentic.llm.llm_tools_decorator import llm_tools
from .llm_tools.artist_crud_tools import album_tool_service, track_tool_service, artist_tool_service
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
])
class NxWebMusicArtistPlugin(BasePlugin):
    pass
