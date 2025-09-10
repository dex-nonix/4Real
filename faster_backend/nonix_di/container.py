import inspect
from typing import Type, Callable, Dict, Any

from nonix_di.base import T

InjectDependencyType = Type[T] | Callable[[], T]


class Container:

    def __init__(self):
        self._providers: Dict[Type[T], Dict[str, Any]] = {}
        self._singletons: Dict[Type[T], T] = {}

    def register(self, dependency: InjectDependencyType, singleton: bool = True, intance=None):
        key = dependency
        if not inspect.isclass(dependency) and not callable(dependency):
            raise TypeError("The dependency must be a class or a callable function.")
        if intance:
            self._singletons[dependency] = intance
        self._providers[key] = {'provider': dependency, 'singleton': singleton}

    def resolve(self, dependency: InjectDependencyType) -> T | None:
        if dependency not in self._providers:
            return None

        config = self._providers[dependency]
        provider = config['provider']
        is_singleton = config['singleton']

        if is_singleton:
            if dependency not in self._singletons:
                if inspect.isclass(provider):
                    provider = provider()
                self._singletons[dependency] = provider
            return self._singletons[dependency]
        else:
            if inspect.isclass(provider):
                return provider()
            return provider


_container = Container()
