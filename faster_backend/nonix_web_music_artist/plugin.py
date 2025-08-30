from typing import Dict, Any

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer
from nonix_web.utils.di import Inject
from .services.album import AlbumService
from .services.artist import ArtistService
from .services.rhyme_technique import RhymeTechniqueService
from .services.style import StyleService
from .services.track import TrackService
from .llm_tools.album_tools import artist_list_albums, album_get_info
from .llm_tools.artist_tools import artist_get_info, artist_list_albums as artist_list_albums_func
from .llm_tools.music_tools import track_list_by_album, style_list_all, track_get_info
from .llm_tools.file_tools import file_list_artist_files, file_read_lyrics


class NxWebMusicArtistPlugin(BasePlugin):
    api_services = [
        AlbumService,
        ArtistService,
        RhymeTechniqueService,
        StyleService,
        TrackService,
    ]

    agentic_tool_manager = Inject("AgenticToolManager")

    async def _startup(self, server: "NxWebServer", config: Dict[str, Any]):
        await self._register_llm_tools()

    async def _register_llm_tools(self):
        if not self.agentic_tool_manager:
            self._logger.warning("AgenticToolManager not available, skipping LLM tool registration")
            return

        tools_to_register = [
            ("music:artist_get_info", artist_get_info, "Get detailed information about a specific artist"),
            ("music:artist_list_albums", artist_list_albums_func, "List all albums for a specific artist with basic info"),
            ("album:artist_list_albums", artist_list_albums, "List all albums for a specific artist"),
            ("album:get_info", album_get_info, "Get detailed information about an album"),
            ("track:list_by_album", track_list_by_album, "List all tracks for a specific album"),
            ("track:get_info", track_get_info, "Get detailed information about a specific track"),
            ("style:list_all", style_list_all, "List all available music styles with artist counts"),
            ("file:list_artist_files", file_list_artist_files, "List files for a specific artist, optionally filtered by category"),
            ("file:read_lyrics", file_read_lyrics, "Read lyrics content from a specific file"),
        ]

        for qualified_name, func, description in tools_to_register:
            try:
                self.agentic_tool_manager.register(qualified_name, func)
                self._logger.info(f"Registered LLM tool: {qualified_name}")
            except Exception as e:
                self._logger.error(f"Failed to register tool {qualified_name}: {e}")

        self._logger.info(f"Successfully registered {len(tools_to_register)} LLM tools")
