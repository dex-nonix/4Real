from typing import final

from nonix_di import InjectDependencyType
from nonix_di.base import NxBaseInject, T
from nonix_di.container import _container


def di_resolve( dependency, required = True ):
    resolved_dependency = _container.resolve(dependency)
    if resolved_dependency is None and required:
        raise TypeError(f"Dependency '{dependency.__name__}' is not registered.")
    return resolved_dependency


@final
class NxInject(NxBaseInject[T, InjectDependencyType]):
    def _resolve(self) -> T | None:
        return di_resolve(self.dependency)
