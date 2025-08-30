from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from .services.album import AlbumService
from .services.artist import ArtistService
from .services.rhyme_technique import RhymeTechniqueService
from .services.style import StyleService
from .services.track import TrackService
from .llm_tools.album_tools import album_list_by_artist, album_get_info
from .llm_tools.artist_tools import artist_get_info, artist_list_albums as artist_list_albums_func
from .llm_tools.music_tools import track_list_by_album, style_list_all, track_get_info
from nonix_web_agentic.llm.llm_tool_mixin import LLMToolMixin


class NxWebMusicArtistPlugin(BasePlugin, LLMToolMixin):
    api_services = [
        AlbumService,
        ArtistService,
        RhymeTechniqueService,
        StyleService,
        TrackService,
    ]

    llm_tools = [
        ("music:artist_get_info", artist_get_info, "Get detailed information about a specific artist"),
        ("music:artist_list_albums", artist_list_albums_func, "List all albums for a specific artist with basic info"),
        ("album:list_by_artist", album_list_by_artist, "List all albums for a specific artist with their tracks"),
        ("album:get_info", album_get_info, "Get detailed information about an album"),
        ("track:list_by_album", track_list_by_album, "List all tracks for a specific album"),
        ("track:get_info", track_get_info, "Get detailed information about a specific track"),
        ("style:list_all", style_list_all, "List all available music styles with artist counts"),
    ]
