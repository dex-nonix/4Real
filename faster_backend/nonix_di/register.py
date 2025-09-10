from nonix_di import InjectDependencyType
from nonix_di.container import _container


def di_register(dependency: InjectDependencyType, singleton: bool = True, instance=None):
    _container.register(dependency, singleton, instance)
    return dependency

