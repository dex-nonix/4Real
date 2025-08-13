from __future__ import annotations

from typing import Any, Callable, Dict


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


registry = InternalToolRegistry()


# Example built-ins (can be extended)
def _admin_system_info() -> dict:
    import platform, os
    return {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'cwd': os.getcwd(),
    }


registry.register('admin:system_info', _admin_system_info)


