from typing import final, Callable


from nonix_di.base import T, NxBaseInject
from nonix_di.resolve import NxInject
from .manager import NxPluginManager


@final
class NxInjectPlugin(NxBaseInject[T, str | Callable[[], str]]):
    plugin_manager: NxPluginManager = NxInject(NxPluginManager)

    def _resolve(self) -> T | None:
        resolved_dependency = self.plugin_manager.get_plugin(self.dependency)
        if resolved_dependency is None and self.required:
            raise TypeError(f"Plugin {self.dependency} not loaded!")
        return resolved_dependency
