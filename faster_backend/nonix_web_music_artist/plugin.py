from nonix_web.plugin.base_plugin import BasePlugin, api_services

from nonix_web_agentic.llm.llm_tools_decorator import llm_tools
from .llm_tools.album_tools import album_list_by_artist, album_get_info
from .llm_tools.artist_tools import artist_get_info, artist_list_albums as artist_list_albums_func
from .llm_tools.music_tools import track_list_by_album, style_list_all, track_get_info
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
    ("music:artist_get_info", artist_get_info),
    ("music:artist_list_albums", artist_list_albums_func),
    ("album:list_by_artist", album_list_by_artist),
    ("album:get_info", album_get_info),
    ("track:list_by_album", track_list_by_album),
    ("track:get_info", track_get_info),
    ("style:list_all", style_list_all),
])
class NxWebMusicArtistPlugin(BasePlugin):
    pass
