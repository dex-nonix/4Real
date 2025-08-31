import inspect
from abc import ABC, abstractmethod
from typing import Type, Callable, Any, Dict, TypeVar, Generic, final

T = TypeVar('T')
TTT = TypeVar('TTT')


class BaseInject(ABC, Generic[T, TTT]):
    def __init__(self, dependency: TTT, required: bool = True):
        self.dependency = dependency
        self.required = required
        self._private_name = f"_{self.__class__.__name__}_{id(self)}"

    def __get__(self, instance, owner) -> T | None:
        if instance is None:
            return self
        if hasattr(instance, self._private_name):
            return getattr(instance, self._private_name)
        resolved_dependency = self._resolve()
        setattr(instance, self._private_name, resolved_dependency)
        return resolved_dependency

    @abstractmethod
    def _resolve(self) -> T | None:
        pass


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


def di_register(dependency: InjectDependencyType, singleton: bool = True, instance=None):
    _container.register(dependency, singleton, instance)
    return dependency

def di_resolve( dependency, required = True ):
    resolved_dependency = _container.resolve(dependency)
    if resolved_dependency is None and required:
        raise TypeError(f"Dependency '{dependency.__name__}' is not registered.")
    return resolved_dependency

@final
class Inject(BaseInject[T, InjectDependencyType]):
    def _resolve(self) -> T | None:
        return di_resolve(self.dependency)

        # resolved_dependency = _container.resolve(self.dependency)
        # if resolved_dependency is None and self.required:
        #     raise TypeError(f"Dependency {self.dependency.__name__} is not registered.")
        # return resolved_dependency
