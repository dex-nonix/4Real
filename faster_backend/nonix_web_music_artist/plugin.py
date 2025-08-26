from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from nonix_web_music_artist.services.album import AlbumService
from nonix_web_music_artist.services.artist import ArtistService
from nonix_web_music_artist.services.rhyme_technique import RhymeTechniqueService
from nonix_web_music_artist.services.style import StyleService
from nonix_web_music_artist.services.track import TrackService


class NxWebMusicArtistPlugin(BasePlugin):
    api_services = [
        AlbumService,
        ArtistService,
        RhymeTechniqueService,
        StyleService,
        TrackService,
    ]

    async def _load_plugin(self, server: NxWebServer, config: Dict[str, Any]):
        pass
