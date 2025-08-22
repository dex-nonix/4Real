from __future__ import annotations

from typing import Any, Callable, Dict

from .tools.album_tools import album_list_tracks, album_get_info
from .tools.artist_tools import artist_list_albums, artist_get_info
from .tools.file_tools import file_list_artist_files, file_read_lyrics
from .tools.music_tools import track_list_by_album, track_get_info, style_list_all


class InternalToolRegistry:
    """Minimal in-process registry mapping qualified tool names to callables."""

    def __init__(self) -> None:
        self._registry: Dict[str, Callable[..., Any]] = {}

    def register(self, qualified_name: str, func: Callable[..., Any]) -> None:
        self._registry[qualified_name] = func

    def get(self, qualified_name: str) -> Callable[..., Any] | None:
        return self._registry.get(qualified_name)

    def list(self) -> Dict[str, Callable[..., Any]]:
        return dict(self._registry)

    async def execute(self, qualified_name: str, args: dict | None = None) -> dict:
        func = self.get(qualified_name)
        if not func:
            return {'status': 'error', 'error': f'tool {qualified_name} not found'}
        try:
            result = func(**(args or {})) if args else func()
            return {'status': 'success', 'result': result}
        except Exception as exc:  # noqa: BLE001
            return {'status': 'error', 'error': str(exc)}


registry = InternalToolRegistry()


# Admin tools
async def _admin_system_info() -> dict:
    import platform, os
    return {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'cwd': os.getcwd(),
    }


# Register admin tools
registry.register('admin:system_info', _admin_system_info)

# Register artist tools
registry.register('artist:list_albums', artist_list_albums)
registry.register('artist:get_info', artist_get_info)

# Register album tools
registry.register('album:list_tracks', album_list_tracks)
registry.register('album:get_info', album_get_info)

# Register file tools
registry.register('file:list_artist_files', file_list_artist_files)
registry.register('file:read_lyrics', file_read_lyrics)

# Register music tools
registry.register('track:list_by_album', track_list_by_album)
registry.register('track:get_info', track_get_info)
registry.register('style:list_all', style_list_all)
