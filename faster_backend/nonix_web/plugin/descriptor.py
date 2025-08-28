from nonix_web.utils.di import Inject
from .plugin_manager import PluginManager


class InjectPlugin:
    plugin_manager: PluginManager = Inject(PluginManager)

    def __init__(self, plugin_name: str, required: bool = True):
        self.plugin_name = plugin_name
        self.required = required
        self._private_name = f"_{plugin_name}_{id(self)}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if hasattr(instance, self._private_name):
            return getattr(instance, self._private_name)
        resolved_dependency = self._resolve()

        setattr(instance, self._private_name, resolved_dependency)
        return resolved_dependency

    def _resolve(self) -> T | None:
        resolved_dependency = self.plugin_manager.get_plugin(self.plugin_name)
        if resolved_dependency is None and self.required:
            raise TypeError(f"Plugin {self.dependency.__name__} not loaded!")
        return resolved_dependency
