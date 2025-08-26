from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from .services.album import AlbumService
from .services.artist import ArtistService
from .services.rhyme_technique import RhymeTechniqueService
from .services.style import StyleService
from .services.track import TrackService


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
