from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')
TTT = TypeVar('TTT')


class NxBaseInject(ABC, Generic[T, TTT]):
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
