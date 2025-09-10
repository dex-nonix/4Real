from typing import final, Callable

from nonix_di.di import BaseInject, T, Inject
from .plugin_manager import PluginManager


@final
class InjectPlugin(BaseInject[T, str | Callable[[], str]]):
    plugin_manager: PluginManager = Inject(PluginManager)

    def _resolve(self) -> T | None:
        resolved_dependency = self.plugin_manager.get_plugin(self.dependency)
        if resolved_dependency is None and self.required:
            raise TypeError(f"Plugin {self.dependency} not loaded!")
        return resolved_dependency
